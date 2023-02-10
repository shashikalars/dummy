#!/usr/bin/env python
__author__ = "Chetan Kumar PG"
__email__  = "cpg@infoblox.com"

#############################################################################
#  Grid Set up required:                                                    #
#  1. GM + Member                                                           #
#  2. Licenses : DNS, Grid, NIOS                                            #
#  3. Enable DNS services                                                   #
#############################################################################

import os
import re
import sys
import config
import pytest
import unittest
import logging
import json
import shlex
import pexpect
import paramiko
from time import sleep
from scp import SCPClient
from subprocess import Popen, PIPE
import ib_utils.ib_NIOS as ib_NIOS
from ib_utils.log_capture import log_action as log
from ib_utils.log_validation import log_validation as logv
from ipaddress import ip_address, IPv4Address, IPv6Address
logging.basicConfig(format='%(asctime)s - %(name)s(%(process)d) - %(levelname)s - %(message)s',filename="sptyrfe_49.log" ,level=logging.DEBUG,filemode='w')

def display_msg(x="",is_dict=False):
    """ 
    This function prints and logs data 'x'.
    is_dict : If this parameter is True, then print the data in easy to read format.
    """
    logging.info(x)
    if is_dict:
        print(json.dumps(x,sort_keys=False, indent=4))
    else:
        print(x)

def is_grid_alive(grid=config.grid_vip):
    """
    Checks whether the grid is reachable
    """
    ping = os.popen("ping -c 2 "+grid).read()
    display_msg(ping)
    if "0 received" in ping:
        return False
    else:
        return True

def remove_known_hosts_file():
    """
    Removes known_hosts file.
    This is to avoid host key expiration issues.
    """
    cmd = "rm -rf /home/"+config.client_username+"/.ssh/known_hosts"
    ret_code = os.system(cmd)
    if ret_code == 0:
        display_msg("Cleared known hosts file")
    else:
        display_msg("Couldnt clear known hosts file")

def restart_services(grid=config.grid_vip, service=['ALL']):
    """
    Restart Services
    """
    display_msg()
    display_msg("+----------------------------------------------+")
    display_msg("|           Restart Services                   |")
    display_msg("+----------------------------------------------+")
    get_ref =  ib_NIOS.wapi_request('GET', object_type="grid",grid_vip=grid)
    ref = json.loads(get_ref)[0]['_ref']
    data= {"mode" : "SIMULTANEOUS","restart_option":"FORCE_RESTART","services": service}
    restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices", fields=json.dumps(data),grid_vip=grid)
    if restart != '{}':
        display_msg(restart)
        display_msg("FAIL: Restart services failed, Please debug above error message for root cause")
        assert False
    sleep(20)
        

def bfd_template(name='bfdtemp',authentication_key='',authentication_key_id=1,authentication_type='',min_rx_interval='',min_tx_interval='',multiplier=''):
    '''
    Add BFD Template
    '''
    display_msg()
    display_msg("+----------------------------------------------+")
    display_msg("|               Add BFD Template               |")
    display_msg("+----------------------------------------------+")
    display_msg("Adding BFD Template : "+name)
    data = {"name":name}
    if authentication_type:
        if authentication_key:
            data["authentication_type"] = authentication_type
            data["authentication_key"] = authentication_key
            data["authentication_key_id"] = authentication_key_id
        else:
            display_msg("An authentication_key must be specified")
    if min_rx_interval:
        data["min_rx_interval"] = min_rx_interval
    if min_tx_interval:
        data["min_tx_interval"] = min_tx_interval
    if multiplier != '':
        data["detection_multiplier"] = multiplier
    display_msg("Data: ")
    display_msg(data, is_dict=True)
    response = ib_NIOS.wapi_request('POST', object_type='bfdtemplate', fields=json.dumps(data))
    if type(response) == tuple:
        display_msg(json.loads(response[1])['text'])
        display_msg("FAIL: Failed to add bfd template. Debug above log messages to find the root cause")
        return False
    else:
        display_msg(response)
        display_msg("PASS: Successfully added bfd template")
        return True

def add_anycast_interface(address,connectivity_type='ipv4',interface='LOOPBACK',bgp=False,ospf=False,fqdn=config.grid_fqdn):
    '''
    Add Anycast Interface
    '''
    display_msg()
    display_msg("+----------------------------------------------+")
    display_msg("|           Add Anycast Interface              |")
    display_msg("+----------------------------------------------+")
    get_ref = ib_NIOS.wapi_request('GET', object_type='member?_return_fields=additional_ip_list')
    display_msg(get_ref)
    flag = False
    for ref in json.loads(get_ref):
        if fqdn in ref['_ref']:
            flag = True
            break
    if not flag:
        display_msg("FAIL: FQDN provided is not found on this grid.")
        display_msg(fqdn)
        assert False
    
    old_data = ref["additional_ip_list"]
    data={"additional_ip_list": [
        {
            "anycast": True,
            "enable_bgp": bgp,
            "enable_ospf": ospf,
            "interface": interface,
        }
    ]}
    if connectivity_type=='ipv4':
        data["additional_ip_list"][0]["ipv4_network_setting"] = {
            "address": address,
            "dscp": 0,
            "primary": False,
            "subnet_mask": "255.255.255.255",
            "use_dscp": False
        
        }
    elif connectivity_type=='ipv6':
        data["additional_ip_list"][0]["ipv6_network_setting"] = {
            "cidr_prefix": 128,
            "dscp": 0,
            "enabled": True,
            "primary": False,
            "use_dscp": False,
            "virtual_ip": address
        }
    data["additional_ip_list"].extend(old_data)
    if not address:
        data = {"additional_ip_list": []}
    display_msg("DATA: ")
    display_msg(data, is_dict=True)
    response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data))
    if type(response) == tuple:
        display_msg(json.loads(response[1])['text'])
        display_msg("FAIL: Failed to add anycast interface. Debug above log messages to find the root cause")
        return False
    else:
        display_msg(response)
        display_msg("PASS: Successfully added anycast interface")
        return True

def configure_anycast_ospf(area_id="0.0.0.12",fqdn=config.grid_fqdn,is_ipv4=True,bfd_template='',hello_interval=10,dead_interval=40):
    '''
    Configure Anycast OSPF
    '''
    display_msg()
    display_msg("+----------------------------------------------+")
    display_msg("|           Configure Anycast OSPF             |")
    display_msg("+----------------------------------------------+")
    get_ref = ib_NIOS.wapi_request('GET', object_type='member?_return_fields=ospf_list')
    display_msg(get_ref)
    flag =False
    for ref in json.loads(get_ref):
        if fqdn in ref['_ref']:
            flag = True
            break
    if not flag:
        display_msg("FAIL: FQDN provided is not found on this grid.")
        display_msg(fqdn)
        assert False
    
    old_data = ref["ospf_list"]
    data={"ospf_list": [ {
                "area_id": area_id,
                "area_type": "STANDARD",
                "authentication_type": 'NONE',
                "auto_calc_cost_enabled": True,
                "cost": 1,
                "dead_interval": dead_interval,
                "enable_bfd": False,
                "hello_interval": hello_interval,
                "interface": "LAN_HA",
                "is_ipv4": is_ipv4,
                "key_id": 1,
                "retransmit_interval": 5,
                "transmit_delay": 1
            }
        ]}
    if bfd_template:
        data["ospf_list"][0]["enable_bfd"] = True
        data["ospf_list"][0]["bfd_template"] = bfd_template

    if old_data:
        if not old_data[0]["is_ipv4"] == data["ospf_list"][0]["is_ipv4"]:
            data["ospf_list"].extend(old_data)
    if not area_id:
        data = {"ospf_list":[]}
    display_msg("DATA: ")
    display_msg(data, is_dict=True)
    response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data))
    if type(response) == tuple:
        display_msg(json.loads(response[1])['text'])
        display_msg("FAIL: Failed to configure anycast OSPF. Debug above log messages to find the root cause")
        return False
    else:
        display_msg(response)
        display_msg("PASS: Successfully configured anycast OSPF")
        return True

def configure_anycast_bgp(bgp_as=12,neighbor_ip=config.anycast_client,fqdn=config.grid_fqdn,keepalive=4,holddown=16,bfd_template=''):
    '''
    Configure Anycast BGP
    '''
    display_msg()
    display_msg("+----------------------------------------------+")
    display_msg("|           Configure Anycast BGP              |")
    display_msg("+----------------------------------------------+")
    get_ref = ib_NIOS.wapi_request('GET', object_type='member?_return_fields=bgp_as')
    display_msg(get_ref)
    flag = False
    for ref in json.loads(get_ref):
        if fqdn in ref['_ref']:
            flag = True
            break
    if not flag:
        display_msg("FAIL: FQDN provided is not found on this grid.")
        display_msg(fqdn)
        assert False
    
    old_data = ref["bgp_as"]
    data={"bgp_as": [
        {
            "as": bgp_as,
            "holddown": holddown,
            "keepalive": keepalive,
            "link_detect": False,
            "neighbors": [
                {
                    "authentication_mode": 'NONE',
                    "enable_bfd": False,
                    "interface": "LAN_HA",
                    "multihop": False,
                    "multihop_ttl": 255,
                    "neighbor_ip": neighbor_ip,
                    "remote_as": bgp_as
                }
            ]
        }
    ]}
    if bfd_template:
        data["bgp_as"][0]["neighbors"][0]["enable_bfd"] = True
        data["bgp_as"][0]["neighbors"][0]["bfd_template"] = bfd_template
    
    if old_data:
        if bgp_as == old_data[0]["as"]:
            if neighbor_ip not in str(old_data[0]["neighbors"]):
                data["bgp_as"][0]["neighbors"].extend(old_data[0]["neighbors"])
    if not bgp_as:
        data = {"bgp_as":[]}
    display_msg("DATA: ")
    display_msg(data, is_dict=True)
    response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data))
    if type(response) == tuple:
        display_msg(json.loads(response[1])['text'])
        display_msg("FAIL: Failed to configure anycast BGP. Debug above log messages to find the root cause")
        return False
    else:
        display_msg(response)
        display_msg("PASS: Successfully configured anycast BGP")
        return True

def add_listen_on_ip_addresses(address, fqdn=config.grid_fqdn):
    '''
    Add Anycast IP addresses to Listen On list of Member DNS Properties
    '''
    display_msg()
    display_msg("+----------------------------------------------+")
    display_msg("|          Add Listen On Addresses             |")
    display_msg("+----------------------------------------------+")
    get_ref = ib_NIOS.wapi_request('GET', object_type='member:dns?_return_fields=additional_ip_list')
    display_msg(get_ref)
    flag =False
    for ref in json.loads(get_ref):
        if fqdn in ref['_ref']:
            flag = True
            break
    if not flag:
        display_msg("FAIL: FQDN provided is not found on this grid.")
        display_msg(fqdn)
        assert False
    data = ref["additional_ip_list"]
    data.append(address)
    if not address:
        data=[]
    data={"additional_ip_list": data}
    display_msg("DATA: ")
    display_msg(data, is_dict=True)
    response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data))
    if type(response) == tuple:
        display_msg(json.loads(response[1])['text'])
        display_msg("FAIL: Failed to add anycast address to listen on list. Debug above log messages to find the root cause")
        return False
    else:
        display_msg(response)
        restart_services()
        display_msg("PASS: Successfully added anycast address to listen on list")
        return True

def modify_and_restart_bird_process(connectivity_type='ipv4',anycast_client=config.anycast_client,area_id='',bgp_as='12',bgp_neighbor=config.grid_vip,neighbor_as=''):
    '''
    Update the bird config file and restart bird process.
    '''
    display_msg()
    display_msg("+----------------------------------------------+")
    display_msg("|          Update bird config file             |")
    display_msg("+----------------------------------------------+")
    if connectivity_type == 'ipv4':
        file = 'bird.conf'
    elif connectivity_type == 'ipv6':
        file = 'bird6.conf'
    else:
        display_msg("Provide valid connectivity type : ipv4/ipv6")
        assert False
    
    # Updating the file
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(config.anycast_client, username='root', password = 'infoblox', timeout=300)
    stdin, stdout, stderr = client.exec_command("cat /usr/local/etc/"+file)
    all_lines = ''
    for line in stdout.readlines():
        if 'area' in line:
            if area_id:
                line = '        area '+area_id+' {\n'
        if 'local as' in line:
            line = '       local as '+bgp_as+';\n'
        if 'neighbor' in line:
            if not neighbor_as:
                neighbor_as = bgp_as
            line = '       neighbor '+bgp_neighbor+' as '+neighbor_as+';\n'
        if 'source address' in line:
            line = '       source address '+anycast_client+';   # What local address we use for the TCP connection\n'
        all_lines += line
    new_lines = all_lines.encode('ascii','ignore')
    display_msg('Modified file')
    display_msg("----------------------------------------------")
    display_msg(new_lines)
    display_msg("----------------------------------------------")

    with open(file, 'w') as f:
        f.write(new_lines)
    
    # Copying the new file
    scp = SCPClient(client.get_transport())
    filepath = '/usr/local/etc/'+file
    localpath = os.getcwd()+'/'+file
    scp.put(localpath, filepath)
    scp.close()
    client.close()
    
    # Clean the file
    os.system("rm -rf "+file)
    
    # restarting the bird process
    bird = file.split('.')[0]
    client1 = paramiko.SSHClient()
    client1.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client1.connect(config.anycast_client, username='root', password = 'infoblox', timeout=300)
    stdin, stdout, stderr = client1.exec_command("pidof "+bird)
    pid = stdout.read()
    display_msg("PID: "+pid)
    stdin, stdout, stderr = client1.exec_command("ps ax | grep bird")
    display_msg(stdout.read())
    if pid:
        stdin, stdout, stderr = client1.exec_command("kill -9 "+pid)
        display_msg(stdout.read())
        display_msg(stderr.read())
    stdin, stdout, stderr = client1.exec_command(bird+" -c /usr/local/etc/"+file)
    display_msg(stdout.read())
    display_msg(stderr.read())
    client1.close()
    display_msg("Sleep for 3 minutes")
    sleep(200)
    
    # validation
    display_msg()
    display_msg("+------------------------------------------+")
    display_msg("|           Validation                     |")
    display_msg("+------------------------------------------+")
    client2 = paramiko.SSHClient()
    client2.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client2.connect(config.anycast_client, username='root', password = 'infoblox', timeout=300)
    stdin, stdout, stderr = client2.exec_command("ps ax | grep bird")
    display_msg(stdout.read())
    stdin, stdout, stderr = client2.exec_command("pidof "+bird)
    pid = stdout.read()
    client2.close()
    if pid:
        display_msg("Bird process started successfully")
        return True
    else:
        display_msg("Bird process not found")
        return False

def validate_routes(address):
    '''
    Validate if the routes are added for the specified anyacast 'address'
    '''
    display_msg("Search for: "+str(address))
    if type(ip_address(unicode(address, "utf-8"))) == IPv4Address:
        cmd = 'route -n'
    elif type(ip_address(unicode(address, "utf-8"))) == IPv6Address:
        cmd = 'route -6 -n'
    else:
        display_msg("FAIL: Invalid address")
        return False
    c = 0
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(config.anycast_client, username='root', password = 'infoblox')
    while c <= 12:
        stdin, stdout, stderr = client.exec_command(cmd)
        routes = stdout.read()
        display_msg(routes)
        if address in routes:
            display_msg("PASS: Routes are added for the given address")
            client.close()
            return True
        display_msg("Sleeping for 10 seconds...")
        sleep(10)
        c += 1
    client.close()
    display_msg("PASS: Routes are not found for the given address even after 1 minute")
    return False

def validate_anycast_service(address,record='a.test.com',lookfor='10.1.1.1'):
    '''
    Perform dig operation and validate anycast service
    '''
    remove_known_hosts_file()
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(config.anycast_client, username='root', password = 'infoblox')
    stdin, stdout, stderr = client.exec_command("dig @"+address+" "+record+" IN A")
    output=stdout.read()
    client.close()
    display_msg(output)
    if lookfor not in output:
        display_msg("FAIL: Dig operation failed with anyacst interface")
        return False
    display_msg("PASS: Dig operation succeeded with expected result")
    return True
    
def generate_token_from_file(filepath, filename,grid=config.grid_vip):
    dir_name=filepath
    base_filename=filename
    filename= os.path.join(dir_name, base_filename)
    data = {"filename":base_filename}
    create_file = ib_NIOS.wapi_request('POST', object_type="fileop",fields=json.dumps(data),params="?_function=uploadinit",grid_vip=grid)
    logging.info(create_file)
    res = json.loads(create_file)
    token = json.loads(create_file)['token']
    url = json.loads(create_file)['url']
    print create_file
    print res
    print token
    print url
    os.system('curl -k1 -u admin:infoblox -F name=%s -F filedata=@%s %s'%(filename,filename,url))
    filename="/"+filename
    return token

def map_remote_user_to_the_group(group='admin-group'):
    '''
    Map remote user to local group
    '''
    display_msg("Selecting remote user to be mapped to the group "+group)
    response = ib_NIOS.wapi_request("GET",object_type="authpolicy")
    auth_policy_ref = json.loads(response)[0]['_ref']
    data={"default_group": group}
    response = ib_NIOS.wapi_request('PUT', ref=auth_policy_ref, fields=json.dumps(data), grid_vip=config.grid_vip)
    display_msg(response)
    if bool(re.match("\"authpolicy*.",str(response))):
        display_msg("Selected '"+group+"' for remote user mapping successfully")
        return True
    else:
        display_msg("Selecting '"+group+"' for remote user mapping failed")
        return False

def get_conf_file(file, grid=config.grid_vip):
    '''
    Returns conf file in list formatt
    '''
    remove_known_hosts_file()
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
    mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
    client.connect(grid, username='root', pkey = mykey)
    display_msg("cat /infoblox/var/quagga/"+file)
    stdin, stdout, stderr = client.exec_command("cat /infoblox/var/quagga/"+file)
    conf_file = []
    for line in stdout.readlines():
        line = line.encode('ascii','ignore')
        conf_file.append(line)
    client.close()
    return conf_file

def check_bfd_status(user='admin', password='infoblox', grid=config.grid_vip):
    '''
    Execute 'show bfd' CLI and returns 
    True - If bfd is up
    False - If bfd is down/not running
    '''
    remove_known_hosts_file()
    try:
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no '+user+'@'+grid)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline(password)
        child.expect('Infoblox >')
        child.sendline('show bfd')
        child.sendline('q')
        child.expect('Infoblox >')
        output=child.before
        child.sendline('exit')
    except Exception as E:
        display_msg("Exception: ")
        display_msg(E)
        assert False
    finally:
        child.close()
    output=output.decode('utf-8')
    output=output.split('\n')
    display_msg(output)
    #if len(output)
    if ' Up ' in output[2]:
        return True
    return False

class SPTYRFE_49(unittest.TestCase):
    
    @pytest.mark.run(order=1)
    def test_001_Add_BFD_template(self):
        """
        Add BFD template with default values.
        """
        display_msg()
        display_msg("+------------------------------------------+")
        display_msg("|           Test Case 1 Started            |")
        display_msg("+------------------------------------------+")
        
        display_msg("Add BFD Template")
        result = bfd_template(name='bfdtemp1')
        if not result:
            assert False
        
        # Validation
        display_msg()
        display_msg("+------------------------------------------+")
        display_msg("|           Validation                     |")
        display_msg("+------------------------------------------+")
        bfd_ref = ib_NIOS.wapi_request('GET', object_type='bfdtemplate', params='?name=bfdtemp1')
        display_msg(bfd_ref)
        if 'bfdtemp1' in bfd_ref:
            display_msg("PASS: BFD template found")
        else:
            display_msg("FAIL: BFD template not found")
            assert False

        display_msg("---------Test Case 1 Execution Completed----------")

    @pytest.mark.run(order=2)
    def test_002_Start_DNS_service(self):
        """
        Start DNS service on all members.
        """
        display_msg()
        display_msg("+----------------------------------------------+")
        display_msg("|           Test Case 2 Started                |")
        display_msg("+----------------------------------------------+")
        
        display_msg("Enable DNS service")
        get_ref = ib_NIOS.wapi_request('GET', object_type='member:dns')
        display_msg(get_ref)
        for ref in json.loads(get_ref):
            response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps({"enable_dns":True,"use_lan_ipv6_port":True}))
            if type(response) == tuple:
                display_msg("FAIL: Enable DNS Service")
                assert False
        restart_services()
        display_msg("PASS: DNS Service enabled")
        
        # Validation
        display_msg()
        display_msg("+------------------------------------------+")
        display_msg("|           Validation                     |")
        display_msg("+------------------------------------------+")
        dns_ref = ib_NIOS.wapi_request('GET', object_type='member:dns?_return_fields=enable_dns')
        display_msg(dns_ref)
        if 'true' in dns_ref:
            display_msg("PASS: DNS service vaidation")
        else:
            display_msg("FAIL: DNS service vaidation")
            assert False
        
        display_msg("---------Test Case 2 Execution Completed----------")
    
    @pytest.mark.run(order=3)
    def test_003_add_auth_zone(self):
        """
        Add an authoritative zone.
        """
        display_msg()
        display_msg("+----------------------------------------------+")
        display_msg("|           Test Case 3 Started                |")
        display_msg("+----------------------------------------------+")
        
        display_msg("Add an authoritative zone test.com")
        data = {"fqdn": "test.com",
                "view":"default",
                "grid_primary": [{"name": config.grid_fqdn,"stealth": False}],
                "grid_secondaries": [{"name":config.grid_member1_fqdn}]}
        response = ib_NIOS.wapi_request('POST',object_type="zone_auth",fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            display_msg("FAIL: Create Authorative FMZ")
            assert False
        restart_services()
        display_msg("PASS: Authoritative zone test.com is added")
        
        # Validation
        display_msg()
        display_msg("+------------------------------------------+")
        display_msg("|           Validation                     |")
        display_msg("+------------------------------------------+")
        get_ref = ib_NIOS.wapi_request('GET',object_type="zone_auth?fqdn=test.com")
        display_msg(get_ref)
        if 'test.com' in get_ref:
            display_msg("PASS: Zone test.com found")
        else:
            display_msg("FAIL: Zone test.com not found")
            assert False
        
        display_msg("---------Test Case 3 Execution Completed----------")

    @pytest.mark.run(order=4)
    def test_004_add_a_record(self):
        """
        Add a record in the test.com zone.
        """
        display_msg()
        display_msg("+----------------------------------------------+")
        display_msg("|           Test Case 4 Started                |")
        display_msg("+----------------------------------------------+")
        
        display_msg("Add a record a.test.com")
        data = {"name":"a.test.com",
                "ipv4addr":"10.1.1.1"
                }
        response = ib_NIOS.wapi_request('POST',object_type='record:a',fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            display_msg("Failure: Add a record a.test.com")
            assert False
        display_msg("PASS: a record a.test.com added")
        
        # Validation
        display_msg()
        display_msg("+------------------------------------------+")
        display_msg("|           Validation                     |")
        display_msg("+------------------------------------------+")
        get_ref = ib_NIOS.wapi_request('GET',object_type="record:a?name=a.test.com")
        display_msg(get_ref)
        if 'a.test.com' in get_ref:
            display_msg("PASS: A record a.test.com found")
        else:
            display_msg("FAIL: A record a.test.com not found")
            assert False
        
        display_msg("---------Test Case 4 Execution Completed----------")

    @pytest.mark.run(order=5)
    def test_005_test_upper_and_lower_limit_for_Min_Rx_Interval(self):
        """
        Test upper/lower limit of Min Rx Interval.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 5 Execution Started           |")
        display_msg("----------------------------------------------------")
        
        display_msg("Add BFD Template with Min_Rx_Interval lower than value 50")
        result_min = bfd_template(name='bfdtemp2',min_rx_interval=49)
        if result_min:
            assert False
        
        display_msg()
        display_msg("Add BFD Template with Min_Rx_Interval greater than value 9999")
        result_max = bfd_template(name='bfdtemp2',min_rx_interval=10000)
        if result_max:
            assert False
        
        # Validation
        display_msg()
        display_msg("+------------------------------------------+")
        display_msg("|           Validation                     |")
        display_msg("+------------------------------------------+")
        bfd_ref = ib_NIOS.wapi_request('GET', object_type='bfdtemplate', params='?name=bfdtemp2')
        display_msg(bfd_ref)
        if 'bfdtemp2' not in bfd_ref:
            display_msg("PASS: BFD template not found")
        else:
            display_msg("FAIL: BFD template found")
            assert False

        display_msg("---------Test Case 5 Execution Completed----------")

    @pytest.mark.run(order=6)
    def test_006_test_upper_and_lower_limit_for_Min_Tx_Interval(self):
        """
        Test upper/lower limit of Min Tx Interval.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 6 Execution Started           |")
        display_msg("----------------------------------------------------")
        
        display_msg("Add BFD Template with Min_Tx_Interval lower than value 50")
        result_min = bfd_template(name='bfdtemp3',min_tx_interval=48)
        if result_min:
            assert False
        
        display_msg()
        display_msg("Add BFD Template with Min_Tx_Interval greater than value 9999")
        result_max = bfd_template(name='bfdtemp3',min_tx_interval=99999)
        if result_max:
            assert False
        
        # Validation
        display_msg()
        display_msg("+------------------------------------------+")
        display_msg("|           Validation                     |")
        display_msg("+------------------------------------------+")
        bfd_ref = ib_NIOS.wapi_request('GET', object_type='bfdtemplate', params='?name=bfdtemp3')
        display_msg(bfd_ref)
        if 'bfdtemp3' not in bfd_ref:
            display_msg("PASS: BFD template not found")
        else:
            display_msg("FAIL: BFD template found")
            assert False

        display_msg("---------Test Case 6 Execution Completed----------")

    @pytest.mark.run(order=7)
    def test_007_test_upper_and_lower_limit_for_Multiplier(self):
        """
        Test upper/lower limit of Multiplier.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 7 Execution Started           |")
        display_msg("----------------------------------------------------")
        
        display_msg("Add BFD Template with Multiplier lower than value 3")
        result_min = bfd_template(name='bfdtemp4',multiplier=0)
        if result_min:
            assert False
        
        display_msg()
        display_msg("Add BFD Template with multiplier greater than value 50")
        result_max = bfd_template(name='bfdtemp4',multiplier=52)
        if result_max:
            assert False
        
        # Validation
        display_msg()
        display_msg("+------------------------------------------+")
        display_msg("|           Validation                     |")
        display_msg("+------------------------------------------+")
        bfd_ref = ib_NIOS.wapi_request('GET', object_type='bfdtemplate', params='?name=bfdtemp4')
        display_msg(bfd_ref)
        if 'bfdtemp4' not in bfd_ref:
            display_msg("PASS: BFD template not found")
        else:
            display_msg("FAIL: BFD template found")
            assert False

        display_msg("---------Test Case 7 Execution Completed----------")

    @pytest.mark.run(order=8)
    def test_008_add_bfd_template_with_authtype_MD5(self):
        """
        Add BFD template with Authentication type as MD5.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 8 Execution Started           |")
        display_msg("----------------------------------------------------")
        
        display_msg("Add BFD template with Authentication type as MD5")
        result = bfd_template(name='bfdtemp5',authentication_type='MD5',authentication_key='test',authentication_key_id=1)
        if not result:
            assert False
        
        # Validation
        display_msg()
        display_msg("+------------------------------------------+")
        display_msg("|           Validation                     |")
        display_msg("+------------------------------------------+")
        bfd_ref = ib_NIOS.wapi_request('GET', object_type='bfdtemplate', params='?name=bfdtemp5')
        display_msg(bfd_ref)
        if 'bfdtemp5' in bfd_ref:
            display_msg("PASS: BFD template found")
        else:
            display_msg("FAIL: BFD template not found")
            assert False

        display_msg("---------Test Case 8 Execution Completed----------")

    @pytest.mark.run(order=9)
    def test_009_add_bfd_template_with_authtype_SHA1(self):
        """
        Add BFD template with Authentication type as SHA-1.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 9 Execution Started           |")
        display_msg("----------------------------------------------------")
        
        display_msg("Add BFD template with Authentication type as SHA-1")
        result = bfd_template(name='bfdtemp6',authentication_type='SHA1',authentication_key='test',authentication_key_id=1)
        if not result:
            assert False
        
        # Validation
        display_msg()
        display_msg("+------------------------------------------+")
        display_msg("|           Validation                     |")
        display_msg("+------------------------------------------+")
        bfd_ref = ib_NIOS.wapi_request('GET', object_type='bfdtemplate', params='?name=bfdtemp6')
        display_msg(bfd_ref)
        if 'bfdtemp6' in bfd_ref:
            display_msg("PASS: BFD template found")
        else:
            display_msg("FAIL: BFD template not found")
            assert False

        display_msg("---------Test Case 9 Execution Completed----------")

    @pytest.mark.run(order=10)
    def test_010_add_bfd_template_with_authtype_METICULOUS_MD5(self):
        """
        Add BFD template with Authentication type as METICULOUS-MD5.
        """
        display_msg()
        display_msg("-----------------------------------------------------")
        display_msg("|          Test Case 10 Execution Started           |")
        display_msg("-----------------------------------------------------")
        
        display_msg("Add BFD template with Authentication type as METICULOUS-MD5")
        result = bfd_template(name='bfdtemp7',authentication_type='METICULOUS-MD5',authentication_key='test',authentication_key_id=1)
        if not result:
            assert False
        
        # Validation
        display_msg()
        display_msg("+------------------------------------------+")
        display_msg("|           Validation                     |")
        display_msg("+------------------------------------------+")
        bfd_ref = ib_NIOS.wapi_request('GET', object_type='bfdtemplate', params='?name=bfdtemp7')
        display_msg(bfd_ref)
        if 'bfdtemp7' in bfd_ref:
            display_msg("PASS: BFD template found")
        else:
            display_msg("FAIL: BFD template not found")
            assert False

        display_msg("---------Test Case 10 Execution Completed----------")

    @pytest.mark.run(order=11)
    def test_011_add_bfd_template_with_authtype_METICULOUS_SHA15(self):
        """
        Add BFD template with Authentication type as METICULOUS-SHA1.
        """
        display_msg()
        display_msg("-----------------------------------------------------")
        display_msg("|          Test Case 11 Execution Started           |")
        display_msg("-----------------------------------------------------")
        
        display_msg("Add BFD template with Authentication type as METICULOUS-SHA1")
        result = bfd_template(name='bfdtemp8',authentication_type='METICULOUS-SHA1',authentication_key='test',authentication_key_id=1)
        if not result:
            assert False
        
        # Validation
        display_msg()
        display_msg("+------------------------------------------+")
        display_msg("|           Validation                     |")
        display_msg("+------------------------------------------+")
        bfd_ref = ib_NIOS.wapi_request('GET', object_type='bfdtemplate', params='?name=bfdtemp8')
        display_msg(bfd_ref)
        if 'bfdtemp8' in bfd_ref:
            display_msg("PASS: BFD template found")
        else:
            display_msg("FAIL: BFD template not found")
            assert False

        display_msg("---------Test Case 11 Execution Completed----------")

    @pytest.mark.run(order=12)
    def test_012_configure_anycast_interface_with_ospf_bgp_disabled(self):
        """
        Configure IPV4 Anycast interface.
        """
        display_msg()
        display_msg("-----------------------------------------------------")
        display_msg("|          Test Case 12 Execution Started           |")
        display_msg("-----------------------------------------------------")
        
        display_msg("Add Anycast interface")
        result = add_anycast_interface('11.1.1.2')
        if not result:
            assert False
        
        display_msg("Sleeping for 5 minutes")
        sleep(300)
        count = 0
        while not is_grid_alive():
        
            if count == 5:
                display_msg("Giving up after 5 tries")
                assert False
            display_msg("Sleeping for 1 more minute...")
            sleep(60)
            count += 1
        
        # Validation
        display_msg()
        display_msg("+------------------------------------------+")
        display_msg("|           Validation                     |")
        display_msg("+------------------------------------------+")
        display_msg("Validate added Anycast interface")
        get_ref2 = ib_NIOS.wapi_request('GET', object_type='member?_return_fields=additional_ip_list')
        display_msg(get_ref2)
        if '11.1.1.2' in get_ref2:
            display_msg("PASS: Successfully validated Anycast interface.")
        else:
            display_msg("FAIL: Anycast interface is not found.")
            assert False
        
        display_msg("Add anycast ip address to the listen on list")
        add_listen_on_ip_addresses('11.1.1.2')
        
        # Validation
        display_msg()
        display_msg("+------------------------------------------+")
        display_msg("|           Validation                     |")
        display_msg("+------------------------------------------+")
        get_ref3 = ib_NIOS.wapi_request('GET', object_type='member:dns?_return_fields=additional_ip_list')
        display_msg(get_ref3)
        if '11.1.1.2' in get_ref3:
            display_msg("PASS: Successfully validated listen on ip adddresses.")
        else:
            display_msg("FAIL: Anycast IP address is not found in the listen on list.")
            assert False
        
        display_msg("---------Test Case 12 Execution Completed----------")

    @pytest.mark.run(order=13)
    def test_013_test_upper_and_lower_limit_for_hello_interval_ospf_config(self):
        """
        Test upper/lower limit for hello interval of OSPF config.
        """
        display_msg()
        display_msg("-----------------------------------------------------")
        display_msg("|          Test Case 13 Execution Started           |")
        display_msg("-----------------------------------------------------")
        
        display_msg("Test upper limit for hello interval of OSPF config")
        result_max = configure_anycast_ospf(area_id="0.0.0.1",hello_interval=65536)
        if result_max:
            assert False
        
        display_msg()
        display_msg("Test lower limit for hello interval of OSPF config")
        result_min = configure_anycast_ospf(area_id="0.0.0.1",hello_interval=0)
        if result_min:
            assert False
        
        display_msg("---------Test Case 13 Execution Completed----------")


    @pytest.mark.run(order=14)
    def test_014_test_upper_and_lower_limit_for_dead_interval_ospf_config(self):
        """
        Test upper/lower limit for dead interval of OSPF config.
        """
        display_msg()
        display_msg("-----------------------------------------------------")
        display_msg("|          Test Case 14 Execution Started           |")
        display_msg("-----------------------------------------------------")
        
        display_msg("Test upper limit for dead interval of OSPF config")
        result_max = configure_anycast_ospf(area_id="0.0.0.2",dead_interval=65536)
        if result_max:
            assert False
        
        display_msg()
        display_msg("Test lower limit for dead interval of OSPF config")
        result_min = configure_anycast_ospf(area_id="0.0.0.2",dead_interval=0)
        if result_min:
            assert False
        
        display_msg("---------Test Case 14 Execution Completed----------")

    @pytest.mark.run(order=15)
    def test_015_test_upper_and_lower_limit_for_keep_alive_bgp_config(self):
        """
        Test upper/lower limit for keep alive of BGP config.
        """
        display_msg()
        display_msg("-----------------------------------------------------")
        display_msg("|          Test Case 15 Execution Started           |")
        display_msg("-----------------------------------------------------")
        
        display_msg("Test upper limit for keep alive of BGP config")
        result_max = configure_anycast_bgp(bgp_as=1, keepalive=21846)
        if result_max:
            assert False
        
        display_msg()
        display_msg("Test lower limit for keep alive of BGP config")
        result_min = configure_anycast_bgp(bgp_as=1, keepalive=0)
        if result_min:
            assert False
        
        display_msg("---------Test Case 15 Execution Completed----------")

    @pytest.mark.run(order=16)
    def test_016_test_upper_and_lower_limit_for_hold_down_bgp_config(self):
        """
        Test upper/lower limit for hold down of BGP config.
        """
        display_msg()
        display_msg("-----------------------------------------------------")
        display_msg("|          Test Case 16 Execution Started           |")
        display_msg("-----------------------------------------------------")
        
        display_msg("Test upper limit for hold down of BGP config")
        result_max = configure_anycast_bgp(bgp_as=2 ,holddown=65536)
        if result_max:
            assert False
        
        display_msg()
        display_msg("Test lower limit for hold down of BGP config")
        result_min = configure_anycast_bgp(bgp_as=2, holddown=2)
        if result_min:
            assert False
        
        display_msg("---------Test Case 16 Execution Completed----------")

    @pytest.mark.run(order=17)
    def test_017_check_enable_bfd_dnscheck_field_under_ospf(self):
        """
        Check 'enable_bfd_dnscheck' is present under ospf_list field of member object.
        """
        display_msg()
        display_msg("-----------------------------------------------------")
        display_msg("|          Test Case 17 Execution Started           |")
        display_msg("-----------------------------------------------------")
        
        display_msg("Check 'enable_bfd_dnscheck' is present under ospf_list field of member object.")
        result = configure_anycast_ospf(area_id="0.0.0.3")
        if not result:
            display_msg("FAIL: Configure anycast OSPF failed")
            assert False
        get_ref = ib_NIOS.wapi_request('GET', object_type='member?_return_fields=ospf_list')
        display_msg(get_ref)
        if 'enable_bfd_dnscheck' in get_ref:
            if json.loads(get_ref)[0]['ospf_list'][0]['enable_bfd_dnscheck'] == True:
                display_msg("PASS: enable_bfd_dnscheck field is set to True by default")
            else:
                display_msg("FAIL: enable_bfd_dnscheck field is set to False by default")
                assert False
        else:
            display_msg("FAIL: enable_bfd_dnscheck field is not present under ospf_list field of member object")
            assert False
        
        display_msg("---------Test Case 17 Execution Completed----------")

    @pytest.mark.run(order=18)
    def test_018_check_enable_bfd_dnscheck_field_under_bgp(self):
        """
        Check 'enable_bfd_dnscheck' is present under bgp_as field of member object.
        """
        display_msg()
        display_msg("-----------------------------------------------------")
        display_msg("|          Test Case 18 Execution Started           |")
        display_msg("-----------------------------------------------------")
        
        display_msg("Check 'enable_bfd_dnscheck' is present under bgp_as field of member object.")
        result = configure_anycast_bgp(bgp_as=12)
        if not result:
            display_msg("FAIL: Configure anycast BGP failed")
            assert False
        get_ref = ib_NIOS.wapi_request('GET', object_type='member?_return_fields=bgp_as')
        display_msg(get_ref)
        if 'enable_bfd_dnscheck' in get_ref:
            if json.loads(get_ref)[0]['bgp_as'][0]["neighbors"][0]['enable_bfd_dnscheck'] == True:
                display_msg("PASS: enable_bfd_dnscheck field is set to True by default")
            else:
                display_msg("FAIL: enable_bfd_dnscheck field is set to False by default")
                assert False
        else:
            display_msg("FAIL: enable_bfd_dnscheck field is not present under bgp_as field of member object")
            assert False
        
        display_msg("---------Test Case 18 Execution Completed----------")

    @pytest.mark.run(order=19)
    def test_019_configure_anycast_ospf_ipv4(self):
        """
        Configure IPV4 Anycast interface with OSPF Config and enable BFD.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 19 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Delete existing OSPF config")
        get_ref = ib_NIOS.wapi_request('GET', object_type='member?_return_fields=ospf_list')
        display_msg(get_ref)
        if json.loads(get_ref)[0]['ospf_list']:
            result = ib_NIOS.wapi_request('PUT', object_type=json.loads(get_ref)[0]['_ref'], fields=json.dumps({'ospf_list':[]}))
            display_msg(result)
            if type(result) == tuple:
                display_msg("FAIL: Failed to delete existing OSPF config")
                assert False
        
        display_msg("Add IPV4 OSPF config")
        result1 = configure_anycast_ospf(area_id="0.0.0.12",bfd_template='bfdtemp1')
        if not result1:
            assert False
        
        # Validation
        display_msg()
        display_msg("+------------------------------------------+")
        display_msg("|           Validation                     |")
        display_msg("+------------------------------------------+")
        display_msg("Validate added IPV4 OSPF config")
        get_ref1 = ib_NIOS.wapi_request('GET', object_type='member?_return_fields=ospf_list')
        display_msg(get_ref1)
        if '0.0.0.12' in get_ref1:
            display_msg("PASS: Successfully validated IPV4 OSPF config.")
        else:
            display_msg("FAIL: IPV4 OSPF config is not found.")
            assert False
        
        display_msg("Add IPV4 Anycast interface")
        result2 = add_anycast_interface('1.1.1.1',connectivity_type='ipv4',ospf=True)
        if not result2:
            assert False
        
        display_msg("Sleeping for 5 minutes")
        sleep(300)
        count = 0
        while not is_grid_alive():
            if count == 5:
                display_msg("Giving up after 5 tries")
                assert False
            display_msg("Sleeping for 1 more minute...")
            sleep(60)
            count += 1
        
        # Validation
        display_msg()
        display_msg("+------------------------------------------+")
        display_msg("|           Validation                     |")
        display_msg("+------------------------------------------+")
        display_msg("Validate added IPV4 Anycast interface")
        get_ref2 = ib_NIOS.wapi_request('GET', object_type='member?_return_fields=additional_ip_list')
        display_msg(get_ref2)
        if '1.1.1.1' in get_ref2:
            display_msg("PASS: Successfully validated IPV4 Anycast interface.")
        else:
            display_msg("FAIL: IPV4 Anycast interface is not found.")
            assert False
        
        display_msg("Add anycast ip address to the listen on list")
        result3 = add_listen_on_ip_addresses('1.1.1.1')
        if not result3:
            assert False
        
        # Validation
        display_msg()
        display_msg("+------------------------------------------+")
        display_msg("|           Validation                     |")
        display_msg("+------------------------------------------+")
        get_ref3 = ib_NIOS.wapi_request('GET', object_type='member:dns?_return_fields=additional_ip_list')
        display_msg(get_ref3)
        if '1.1.1.1' in get_ref3:
            display_msg("PASS: Successfully validated listen on ip adddresses.")
        else:
            display_msg("FAIL: Anycast IP address is not found in the listen on list.")
            assert False
        
        # Update bird config and restart bird process
        display_msg("Update the bird config file and restart bird process")
        result4 = modify_and_restart_bird_process(area_id='0.0.0.12')
        if not result4:
            assert False
        
        display_msg("---------Test Case 19 Execution Completed----------")

    @pytest.mark.run(order=20)
    def test_020_validate_ospf_ipv4_anycast_service(self):
        """
        Dig using anycast IP address and validate anycast service
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 20 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Validate routes are added")
        result1 = validate_routes('1.1.1.1')
        if not result1:
            assert False
        display_msg("Perform dig operation using Anycast interface")
        result2 = validate_anycast_service('1.1.1.1')
        if not result2:
            assert False
        
        display_msg("---------Test Case 20 Execution Completed----------")

    @pytest.mark.run(order=21)
    def test_021_validate_bfd_internal_dns_monitoring_is_enabled_by_default_ospf_ipv4(self):
        """
        Check enable_bfd_dnscheck field is set true by default.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 21 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Check enable_bfd_dnscheck field is set true by default")
        result = ib_NIOS.wapi_request('GET', object_type='member?_return_fields=ospf_list')
        display_msg(result)
        if json.loads(result)[0]['ospf_list'][0]['enable_bfd_dnscheck'] == True:
            display_msg("PASS: enable_bfd_dnscheck field is set to True by default")
        else:
            display_msg("FAIL: enable_bfd_dnscheck field is set to False by default")
            assert False
        
        display_msg("Check BFD is Up and Running")
        result = check_bfd_status()
        if not result:
            display_msg("BFD process is not Up or not running")
            assert False
        display_msg("BFD process is Up and Running")
        
        display_msg("---------Test Case 21 Execution Completed----------")

# Anycast OSPF ipv6

    @pytest.mark.run(order=22)
    def test_022_configure_anycast_ospf_ipv6(self):
        """
        Configure IPV6 Anycast interface with OSPF.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 22 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Add IPV6 OSPF config")
        result1 = configure_anycast_ospf(area_id="0.0.0.13",bfd_template='bfdtemp1',is_ipv4=False)
        if not result1:
            assert False
        
        # Validation
        display_msg()
        display_msg("+------------------------------------------+")
        display_msg("|           Validation                     |")
        display_msg("+------------------------------------------+")
        display_msg("Validate added IPV6 OSPF config")
        get_ref1 = ib_NIOS.wapi_request('GET', object_type='member?_return_fields=ospf_list')
        display_msg(get_ref1)
        if '0.0.0.13' in get_ref1:
            display_msg("PASS: Successfully validated IPV6 OSPF config.")
        else:
            display_msg("FAIL: IPV6 OSPF config is not found.")
            assert False
        
        display_msg("Add IPV6 Anycast interface")
        result2 = add_anycast_interface('1111::1111',connectivity_type='ipv6',ospf=True)
        if not result2:
            assert False
        
        display_msg("Sleeping for 5 minutes")
        sleep(300)
        count = 0
        while not is_grid_alive():
            if count == 5:
                display_msg("Giving up after 5 tries")
                assert False
            display_msg("Sleeping for 1 more minute...")
            sleep(60)
            count += 1
        
        # Validation
        display_msg()
        display_msg("+------------------------------------------+")
        display_msg("|           Validation                     |")
        display_msg("+------------------------------------------+")
        display_msg("Validate added IPV6 Anycast interface")
        get_ref2 = ib_NIOS.wapi_request('GET', object_type='member?_return_fields=additional_ip_list')
        display_msg(get_ref2)
        if '1111::1111' in get_ref2:
            display_msg("PASS: Successfully validated IPV6 Anycast interface.")
        else:
            display_msg("FAIL: IPV6 Anycast interface is not found.")
            assert False
        
        display_msg("Add anycast ip address to the listen on list")
        result3 = add_listen_on_ip_addresses('1111::1111')
        if not result3:
            assert False
        
        # Validation
        display_msg()
        display_msg("+------------------------------------------+")
        display_msg("|           Validation                     |")
        display_msg("+------------------------------------------+")
        get_ref3 = ib_NIOS.wapi_request('GET', object_type='member:dns?_return_fields=additional_ip_list')
        display_msg(get_ref3)
        if '1111::1111' in get_ref3:
            display_msg("PASS: Successfully validated listen on ip adddresses.")
        else:
            display_msg("FAIL: Anycast IP address is not found in the listen on list.")
            assert False
        
        # Update bird config and restart bird process
        display_msg("Update the bird config file and restart bird process")
        result4 = modify_and_restart_bird_process(connectivity_type='ipv6',area_id='0.0.0.13',bgp_neighbor=config.grid_vip_v6,anycast_client=config.anycast_client_v6)
        if not result4:
            assert False
        
        display_msg("---------Test Case 22 Execution Completed----------")

    @pytest.mark.run(order=23)
    def test_023_validate_ospf_ipv6_anycast_service(self):
        """
        Dig using anycast IP address and validate anycast service
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 23 Execution Started          |")
        display_msg("----------------------------------------------------")
        display_msg("Validate routes are added")
        result1 = validate_routes('1111::1111')
        if not result1:
            assert False
        display_msg("Perform dig operation using Anycast interface")
        result2 = validate_anycast_service('1111::1111')
        if not result2:
            assert False
        
        display_msg("---------Test Case 23 Execution Completed----------")

    @pytest.mark.run(order=24)
    def test_024_validate_bfd_internal_dns_monitoring_is_enabled_by_default_ospf_ipv6(self):
        """
        Check enable_bfd_dnscheck field is set true by default.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 24 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Check enable_bfd_dnscheck field is set true by default")
        result = ib_NIOS.wapi_request('GET', object_type='member?_return_fields=ospf_list')
        display_msg(result)
        if json.loads(result)[0]['ospf_list'][1]['enable_bfd_dnscheck'] == True:
            display_msg("PASS: enable_bfd_dnscheck field is set to True by default")
        else:
            display_msg("FAIL: enable_bfd_dnscheck field is set to False by default")
            assert False
        
        display_msg("Check BFD is Up and Running")
        result = check_bfd_status()
        if not result:
            display_msg("BFD process is not Up or not running")
            assert False
        display_msg("BFD process is Up and Running")
        
        display_msg("---------Test Case 24 Execution Completed----------")

# Anycast BGP ipv4

    @pytest.mark.run(order=25)
    def test_025_configure_anycast_bgp_ipv4(self):
        """
        Configure IPV4 Anycast interface with BGP.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 25 Execution Started          |")
        display_msg("----------------------------------------------------")
        
        display_msg("Delete existing BGP Neighbor")
        get_ref = ib_NIOS.wapi_request('GET', object_type='member?_return_fields=bgp_as')
        display_msg(get_ref)
        if json.loads(get_ref)[0]['bgp_as']:
            result = ib_NIOS.wapi_request('PUT', ref=json.loads(get_ref)[0]['_ref'], fields=json.dumps({'bgp_as':[]}))
            display_msg(result)
            if type(result) == tuple:
                display_msg("FAIL: Failed to delete existing OSPF config")
                assert False
        
        display_msg("Add BGP config")
        result1 = configure_anycast_bgp(bgp_as=12,bfd_template='bfdtemp1')
        if not result1:
            assert False
        
        # Validation
        display_msg()
        display_msg("+------------------------------------------+")
        display_msg("|           Validation                     |")
        display_msg("+------------------------------------------+")
        display_msg("Validate added BGP config")
        get_ref1 = ib_NIOS.wapi_request('GET', object_type='member?_return_fields=bgp_as')
        display_msg(get_ref1)
        if '12' in get_ref1 and config.anycast_client in get_ref1:
            display_msg("PASS: Successfully validated BGP config.")
        else:
            display_msg("FAIL: BGP config is not found.")
            assert False
        
        display_msg("Add Anycast interface")
        result2 = add_anycast_interface('1.1.1.2',bgp=True)
        if not result2:
            assert False
        
        display_msg("Sleeping for 5 minutes")
        sleep(300)
        count = 0
        while not is_grid_alive():
            if count == 5:
                display_msg("Giving up after 5 tries")
                assert False
            display_msg("Sleeping for 1 more minute...")
            sleep(60)
            count += 1
        
        # Validation
        display_msg()
        display_msg("+------------------------------------------+")
        display_msg("|           Validation                     |")
        display_msg("+------------------------------------------+")
        display_msg("Validate added Anycast interface")
        get_ref2 = ib_NIOS.wapi_request('GET', object_type='member?_return_fields=additional_ip_list')
        display_msg(get_ref2)
        if '1.1.1.2' in get_ref2:
            display_msg("PASS: Successfully validated Anycast interface.")
        else:
            display_msg("FAIL: Anycast interface is not found.")
            assert False
        
        display_msg("Add anycast ip address to the listen on list")
        result3 = add_listen_on_ip_addresses('1.1.1.2')
        if not result3:
            assert False
        
        # Validation
        display_msg()
        display_msg("+------------------------------------------+")
        display_msg("|           Validation                     |")
        display_msg("+------------------------------------------+")
        get_ref3 = ib_NIOS.wapi_request('GET', object_type='member:dns?_return_fields=additional_ip_list')
        display_msg(get_ref3)
        if '1.1.1.2' in get_ref3:
            display_msg("PASS: Successfully validated listen on ip adddresses.")
        else:
            display_msg("FAIL: Anycast IP address is not found in the listen on list.")
            assert False
        
        # Update bird config and restart bird process
        display_msg("Update the bird config file and restart bird process")
        result4 = modify_and_restart_bird_process(bgp_as='12')
        if not result4:
            assert False
        
        display_msg("---------Test Case 25 Execution Completed----------")
        
    @pytest.mark.run(order=26)
    def test_026_validate_bgp_ipv4_anycast_service(self):
        """
        Dig using anycast IP address and validate anycast service
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 24 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Validate routes are added")
        result1 = validate_routes('1.1.1.2')
        if not result1:
            assert False
        display_msg("Perform dig operation using Anycast interface")
        result2 = validate_anycast_service('1.1.1.2')
        if not result2:
            assert False
        
        display_msg("---------Test Case 26 Execution Completed----------")

    @pytest.mark.run(order=27)
    def test_027_validate_bfd_internal_dns_monitoring_is_enabled_by_default_bgp_ipv4(self):
        """
        Check enable_bfd_dnscheck field is set true by default.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 27 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Check enable_bfd_dnscheck field is set true by default")
        result = ib_NIOS.wapi_request('GET', object_type='member?_return_fields=bgp_as')
        display_msg(result)
        if json.loads(result)[0]['bgp_as'][0]["neighbors"][0]['enable_bfd_dnscheck'] == True:
            display_msg("PASS: enable_bfd_dnscheck field is set to True by default")
        else:
            display_msg("FAIL: enable_bfd_dnscheck field is set to False by default")
            assert False
        
        display_msg("Check BFD is Up and Running")
        result = check_bfd_status()
        if not result:
            display_msg("BFD process is not Up or not running")
            assert False
        display_msg("BFD process is Up and Running")
                
        display_msg("---------Test Case 27 Execution Completed----------")

# Anycast BGP ipv6

    @pytest.mark.run(order=28)
    def test_028_configure_anycast_bgp_ipv6(self):
        """
        Configure IPV6 Anycast interface with BGP.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 28 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Add IPV6 BGP config")
        result1 = configure_anycast_bgp(bgp_as=12,bfd_template='bfdtemp1',neighbor_ip=config.anycast_client_v6)
        if not result1:
            assert False
        
        # Validation
        display_msg()
        display_msg("+------------------------------------------+")
        display_msg("|           Validation                     |")
        display_msg("+------------------------------------------+")
        display_msg("Validate added IPV6 BGP config")
        get_ref1 = ib_NIOS.wapi_request('GET', object_type='member?_return_fields=bgp_as')
        display_msg(get_ref1)
        if '12' in get_ref1 and config.anycast_client_v6 in get_ref1:
            display_msg("PASS: Successfully validated IPV6 BGP config.")
        else:
            display_msg("FAIL: IPV6 BGP config is not found.")
            assert False
        
        display_msg("Add IPV6 Anycast interface")
        result2 = add_anycast_interface('2222::2222',bgp=True,connectivity_type='ipv6')
        if not result2:
            assert False
        
        display_msg("Sleeping for 5 minutes")
        sleep(300)
        count = 0
        while not is_grid_alive():
            if count == 5:
                display_msg("Giving up after 5 tries")
                assert False
            display_msg("Sleeping for 1 more minute...")
            sleep(60)
            count += 1
        
        # Validation
        display_msg()
        display_msg("+------------------------------------------+")
        display_msg("|           Validation                     |")
        display_msg("+------------------------------------------+")
        display_msg("Validate added IPV6 Anycast interface")
        get_ref2 = ib_NIOS.wapi_request('GET', object_type='member?_return_fields=additional_ip_list')
        display_msg(get_ref2)
        if '2222::2222' in get_ref2:
            display_msg("PASS: Successfully validated IPV6 Anycast interface.")
        else:
            display_msg("FAIL: IPV6 Anycast interface is not found.")
            assert False
        
        display_msg("Add IPV6 anycast ip address to the listen on list")
        result3 = add_listen_on_ip_addresses('2222::2222')
        if not result3:
            assert False
        
        # Validation
        display_msg()
        display_msg("+------------------------------------------+")
        display_msg("|           Validation                     |")
        display_msg("+------------------------------------------+")
        get_ref3 = ib_NIOS.wapi_request('GET', object_type='member:dns?_return_fields=additional_ip_list')
        display_msg(get_ref3)
        if '2222::2222' in get_ref3:
            display_msg("PASS: Successfully validated listen on ip adddresses.")
        else:
            display_msg("FAIL: IPV6 Anycast IP address is not found in the listen on list.")
            assert False
        
        # Update bird config and restart bird process
        display_msg("Update the bird config file and restart bird process")
        result4 = modify_and_restart_bird_process(bgp_as='12',connectivity_type='ipv6',bgp_neighbor=config.grid_vip_v6,anycast_client=config.anycast_client_v6)
        if not result4:
            assert False
        
        display_msg("---------Test Case 28 Execution Completed----------")
        
    @pytest.mark.run(order=29)
    def test_029_validate_bgp_ipv6_anycast_service(self):
        """
        Dig using anycast IP address and validate anycast service
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 26 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Validate routes are added")
        result1 = validate_routes('2222::2222')
        if not result1:
            assert False
        display_msg("Perform dig operation using Anycast interface")
        result2 = validate_anycast_service('2222::2222')
        if not result2:
            assert False
        
        display_msg("---------Test Case 29 Execution Completed----------")

    @pytest.mark.run(order=30)
    def test_030_validate_bfd_internal_dns_monitoring_is_enabled_by_default_bgp_ipv6(self):
        """
        Check enable_bfd_dnscheck field is set true by default.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 30 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Check enable_bfd_dnscheck field is set true by default")
        result = ib_NIOS.wapi_request('GET', object_type='member?_return_fields=bgp_as')
        display_msg(result)
        if json.loads(result)[0]['bgp_as'][0]["neighbors"][1]['enable_bfd_dnscheck'] == True:
            display_msg("PASS: enable_bfd_dnscheck field is set to True by default")
        else:
            display_msg("FAIL: enable_bfd_dnscheck field is set to False by default")
            assert False
        
        display_msg("Check BFD is Up and Running")
        result = check_bfd_status()
        if not result:
            display_msg("BFD process is not Up or not running")
            assert False
        display_msg("BFD process is Up and Running")
        
        display_msg("---------Test Case 30 Execution Completed----------")

    @pytest.mark.run(order=31)
    def test_031_modify_bfd_template(self):
        """
        Modify BFD template and validate that BFD is restarted.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 31 Execution Started           |")
        display_msg("----------------------------------------------------")
        # Start log capture
        display_msg("Start capturing infoblox.log")
        log("start","/infoblox/var/infoblox.log",config.grid_vip)
        
        display_msg("Update BFD template bfdtemp1 with new values")
        get_ref = ib_NIOS.wapi_request('GET', object_type='bfdtemplate')
        display_msg(get_ref)
        ref = ''
        for temp in json.loads(get_ref):
            if temp['name'] == 'bfdtemp1':
                ref = temp['_ref']
                break
        if not ref:
            display_msg("FAIL: Failed to fetch BFD template with name 'bfdtemp1'")
            assert False

        new_data = {"name":"bfdtemp1",
                    "min_rx_interval":50,
                    "min_tx_interval":50,
                    "detection_multiplier":3}
        response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(new_data))
        if type(response) == tuple:
            display_msg(json.loads(response[1])['text'])
            display_msg("FAIL: Failed to modify bfd template. Debug above log messages to find the root cause")
            assert False
        else:
            display_msg(response)
            display_msg("PASS: Successfully modified bfd template")
        
        sleep(120)
        
        # stop log capture
        display_msg("Stop log capture")
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
        
        # validate captured log
        display_msg("Validate log for BFD restart")
        try:
            logv("\'BFD configuration file has been changed\'","/infoblox/var/infoblox.log",config.grid_vip)
            logv("\'BFD configuration file has been backed up\'","/infoblox/var/infoblox.log",config.grid_vip)
            logv("\'BFD configuration file has been updated\'","/infoblox/var/infoblox.log",config.grid_vip)
            logv("\'Starting bfdd process\'","/infoblox/var/infoblox.log",config.grid_vip)
            logv("\'Starting bgpd process\'","/infoblox/var/infoblox.log",config.grid_vip)
            logv("\'Starting ospfd process\'","/infoblox/var/infoblox.log",config.grid_vip)
            logv("\'Starting ospf6d process\'","/infoblox/var/infoblox.log",config.grid_vip)
        except Exception as E:
            if 'returned non-zero exit status 1' in str(E):
                display_msg("FAIL: Above string is not found in the logs")
                assert False
            display_msg(E)
            assert False
        
        # Validate BFD status
        display_msg("Check BFD is Up and Running")
        result = check_bfd_status()
        if not result:
            display_msg("BFD process is not Up or not running")
            assert False
        display_msg("BFD process is Up and Running")
        
        display_msg("---------Test Case 31 Execution Completed----------")

    @pytest.mark.run(order=32)
    def test_032_Enable_logging_for_queries_and_responses(self):
        """
        Enable queries and response logging.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 32 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Enable queries and response logging")
        get_ref = ib_NIOS.wapi_request('GET', object_type='grid:dns')
        display_msg(get_ref)
        data = {"logging_categories":{"log_queries":True, "log_responses":True}}
        response = ib_NIOS.wapi_request('PUT', ref=json.loads(get_ref)[0]['_ref'], fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            display_msg("FAIL: Failed to enable logging for queries and responses")
            assert False
        
        restart_services()
        
        #Validation
        display_msg()
        display_msg("+------------------------------------------+")
        display_msg("|           Validation                     |")
        display_msg("+------------------------------------------+")
        get_ref = ib_NIOS.wapi_request('GET', object_type='grid:dns?_return_fields=logging_categories')
        display_msg(get_ref)
        if 'log_queries": true' in get_ref and 'log_responses": true' in get_ref:
            display_msg("PASS: Successfully enabled logging for queries and responses")
        else:
            display_msg("FAIL: Failed to enable logging for queries and responses")
            assert False
        
        display_msg("---------Test Case 32 Execution Completed----------")

    @pytest.mark.run(order=33)
    def test_033_validate_bfd_internal_dns_monitoring_by_checking_dns_lookups(self):
        """
        Validate BFD Internal DNS monitoring by checking DNS lookup queries.
        Log Validation
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 33 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Start capturing syslog")
        log("start","/var/log/syslog",config.grid_vip)
        display_msg("Sleeping for 10 seconds")
        sleep(30)
        display_msg("Stop capturing log")
        log("stop","/var/log/syslog",config.grid_vip)
        
        display_msg("Validate captured log for dns lookup queries")
        try:
            # ipv4
            logv("\'127.0.0.1.*query: . IN A - (1.1.1.2)\'","/var/log/syslog",config.grid_vip)
            logv("\'127.0.0.1.*UDP: query: . IN A response: REFUSED\'","/var/log/syslog",config.grid_vip)
            logv("\'127.0.0.1.*query: . IN A - (1.1.1.1)\'","/var/log/syslog",config.grid_vip)
            logv("\'127.0.0.1.*UDP: query: . IN A response: REFUSED\'","/var/log/syslog",config.grid_vip)
            # ipv6
            logv("\'::1.*query: . IN A - (1111::1111)\'","/var/log/syslog",config.grid_vip)
            logv("\'::1.*UDP: query: . IN A response: REFUSED\'","/var/log/syslog",config.grid_vip)
            logv("\'::1.*query: . IN A - (2222::2222)\'","/var/log/syslog",config.grid_vip)
            logv("\'::1.*UDP: query: . IN A response: REFUSED\'","/var/log/syslog",config.grid_vip)
        except Exception as E:
            if 'returned non-zero exit status 1' in str(E):
                display_msg("FAIL: Above string is not found in the logs")
                assert False
            display_msg(E)
            assert False
        
        display_msg("---------Test Case 33 Execution Completed----------")

# Disable BFD Internal DNS Monitoring for OSPF IPV4
    @pytest.mark.run(order=34)
    def test_034_Disable_BFD_Internal_DNS_Monitoring_for_OSPF_ipv4(self):
        """
        Disable BFD Internal DNS Monitoring field and validate no DNS lookup is happening.
        Log Validation
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 34 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Disable BFD Internal DNS Monitoring on ipv4 OSPF interface")
        get_ref = ib_NIOS.wapi_request('GET', object_type='member?_return_fields=ospf_list')
        display_msg(get_ref)
        ref = json.loads(get_ref)[0]['_ref']
        
        old_data = json.loads(get_ref)[0]["ospf_list"]
        to_be_modified = ''
        to_be_kept = ''
        for item in old_data:
            if item['is_ipv4'] == True:
                to_be_modified = item
            elif item['is_ipv4'] == False:
                to_be_kept = item
        if not to_be_modified:
            display_msg("FAIL: Failed to find ipv4 OSPF config")
            assert False
        data={"ospf_list": [{
              "area_id": to_be_modified['area_id'],
              "area_type": to_be_modified['area_type'],
              "authentication_type": to_be_modified['authentication_type'],
              "auto_calc_cost_enabled": to_be_modified['auto_calc_cost_enabled'],
              "cost": to_be_modified['cost'],
              "dead_interval": to_be_modified['dead_interval'],
              "enable_bfd": to_be_modified['enable_bfd'],
              "bfd_template": to_be_modified['bfd_template'],
              "hello_interval": to_be_modified['hello_interval'],
              "interface": to_be_modified['interface'],
              "is_ipv4": to_be_modified['is_ipv4'],
              "key_id": to_be_modified['key_id'],
              "retransmit_interval": to_be_modified['retransmit_interval'],
              "transmit_delay": to_be_modified['transmit_delay'],
              "enable_bfd_dnscheck": False
              }]}
        
        if to_be_kept:
            data["ospf_list"].extend([to_be_kept])
        display_msg("DATA: ")
        display_msg(data, is_dict=True)
        response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(data))
        if type(response) == tuple:
            display_msg(json.loads(response[1])['text'])
            display_msg("FAIL: Failed to update anycast OSPF. Debug above log messages to find the root cause")
            assert False
        else:
            display_msg(response)
            display_msg("PASS: Successfully updated anycast OSPF")
            sleep(120)
        
        display_msg("---------Test Case 34 Execution Completed----------")

    @pytest.mark.run(order=35)
    def test_035_Check_DNS_lookup_stopped_on_ipv4_ospf_interface(self):
        """
        Validate BFD Internal DNS monitoring is disabled on OSPF ipv4 interface by checking DNS lookup queries.
        Log Validation
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 35 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Start capturing syslog")
        log("start","/var/log/syslog",config.grid_vip)
        display_msg("Sleeping for 10 seconds")
        sleep(10)
        display_msg("Stop capturing log")
        log("stop","/var/log/syslog",config.grid_vip)
        
        display_msg("Validate captured log for dns lookup queries")
        try:
            logv("\'127.0.0.1.*query: . IN A - (1.1.1.1)\'","/var/log/syslog",config.grid_vip)
            logv("\'127.0.0.1.*UDP: query: . IN A response: REFUSED\'","/var/log/syslog",config.grid_vip)
            display_msg("FAIL: BFD Internal DNS Monitoring is still active.")
            assert False
        except Exception as E:
            if 'returned non-zero exit status 1' in str(E):
                display_msg("PASS: BFD Internal DNS Monitoring is not active.")
            else:
                display_msg(E)
                assert False
        
        display_msg("---------Test Case 35 Execution Completed----------")

    @pytest.mark.run(order=36)
    def test_036_Enable_BFD_Internal_DNS_Monitoring_for_OSPF_ipv4(self):
        """
        Enable BFD Internal DNS Monitoring field and validate no DNS lookup is happening.
        Log Validation
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 36 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Enable BFD Internal DNS Monitoring on ipv4 OSPF interface")
        get_ref = ib_NIOS.wapi_request('GET', object_type='member?_return_fields=ospf_list')
        display_msg(get_ref)
        ref = json.loads(get_ref)[0]['_ref']
        
        old_data = json.loads(get_ref)[0]["ospf_list"]
        to_be_modified = ''
        to_be_kept = ''
        for item in old_data:
            if item['is_ipv4'] == True:
                to_be_modified = item
            elif item['is_ipv4'] == False:
                to_be_kept = item
        if not to_be_modified:
            display_msg("FAIL: Failed to find ipv4 OSPF config")
            assert False
        data={"ospf_list": [{
              "area_id": to_be_modified['area_id'],
              "area_type": to_be_modified['area_type'],
              "authentication_type": to_be_modified['authentication_type'],
              "auto_calc_cost_enabled": to_be_modified['auto_calc_cost_enabled'],
              "cost": to_be_modified['cost'],
              "dead_interval": to_be_modified['dead_interval'],
              "enable_bfd": to_be_modified['enable_bfd'],
              "bfd_template": to_be_modified['bfd_template'],
              "hello_interval": to_be_modified['hello_interval'],
              "interface": to_be_modified['interface'],
              "is_ipv4": to_be_modified['is_ipv4'],
              "key_id": to_be_modified['key_id'],
              "retransmit_interval": to_be_modified['retransmit_interval'],
              "transmit_delay": to_be_modified['transmit_delay'],
              "enable_bfd_dnscheck": True
              }]}
        
        if to_be_kept:
            data["ospf_list"].extend([to_be_kept])
        display_msg("DATA: ")
        display_msg(data, is_dict=True)
        response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(data))
        if type(response) == tuple:
            display_msg(json.loads(response[1])['text'])
            display_msg("FAIL: Failed to update anycast OSPF. Debug above log messages to find the root cause")
            assert False
        else:
            display_msg(response)
            display_msg("PASS: Successfully updated anycast OSPF")
            sleep(120)
        
        display_msg("---------Test Case 36 Execution Completed----------")

    @pytest.mark.run(order=37)
    def test_037_Check_DNS_lookup_on_ipv4_ospf_interface_is_back(self):
        """
        Validate BFD Internal DNS monitoring is disabled on OSPF ipv4 interface by checking DNS lookup queries.
        Log Validation
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 37 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Start capturing syslog")
        log("start","/var/log/syslog",config.grid_vip)
        display_msg("Sleeping for 10 seconds")
        sleep(10)
        display_msg("Stop capturing log")
        log("stop","/var/log/syslog",config.grid_vip)
        
        display_msg("Validate captured log for dns lookup queries")
        try:
            logv("\'127.0.0.1.*query: . IN A - (1.1.1.1)\'","/var/log/syslog",config.grid_vip)
            logv("\'127.0.0.1.*UDP: query: . IN A response: REFUSED\'","/var/log/syslog",config.grid_vip)
            display_msg("PASS: BFD Internal DNS Monitoring is active.")
        except Exception as E:
            if 'returned non-zero exit status 1' in str(E):
                display_msg("FAIL: BFD Internal DNS Monitoring is not yet active.")
                assert False
            else:
                display_msg(E)
                assert False
        
        display_msg("---------Test Case 37 Execution Completed----------")

# Disable BFD Internal DNS Monitoring for OSPF IPV6
    @pytest.mark.run(order=38)
    def test_038_Disable_BFD_Internal_DNS_Monitoring_for_OSPF_ipv6(self):
        """
        Disable BFD Internal DNS Monitoring field and validate no DNS lookup is happening.
        Log Validation
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 38 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Disable BFD Internal DNS Monitoring on ipv6 OSPF interface")
        get_ref = ib_NIOS.wapi_request('GET', object_type='member?_return_fields=ospf_list')
        display_msg(get_ref)
        ref = json.loads(get_ref)[0]['_ref']
        
        old_data = json.loads(get_ref)[0]["ospf_list"]
        to_be_modified = ''
        to_be_kept = ''
        for item in old_data:
            if item['is_ipv4'] == False:
                to_be_modified = item
            elif item['is_ipv4'] == True:
                to_be_kept = item
        if not to_be_modified:
            display_msg("FAIL: Failed to find ipv6 OSPF config")
            assert False
        data={"ospf_list": [{
              "area_id": to_be_modified['area_id'],
              "area_type": to_be_modified['area_type'],
              "authentication_type": to_be_modified['authentication_type'],
              "auto_calc_cost_enabled": to_be_modified['auto_calc_cost_enabled'],
              "cost": to_be_modified['cost'],
              "dead_interval": to_be_modified['dead_interval'],
              "enable_bfd": to_be_modified['enable_bfd'],
              "bfd_template": to_be_modified['bfd_template'],
              "hello_interval": to_be_modified['hello_interval'],
              "interface": to_be_modified['interface'],
              "is_ipv4": to_be_modified['is_ipv4'],
              "key_id": to_be_modified['key_id'],
              "retransmit_interval": to_be_modified['retransmit_interval'],
              "transmit_delay": to_be_modified['transmit_delay'],
              "enable_bfd_dnscheck": False
              }]}
        
        if to_be_kept:
            data["ospf_list"].extend([to_be_kept])
        display_msg("DATA: ")
        display_msg(data, is_dict=True)
        response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(data))
        if type(response) == tuple:
            display_msg(json.loads(response[1])['text'])
            display_msg("FAIL: Failed to update anycast OSPF. Debug above log messages to find the root cause")
            assert False
        else:
            display_msg(response)
            display_msg("PASS: Successfully updated anycast OSPF")
            sleep(120)
        
        display_msg("---------Test Case 38 Execution Completed----------")

    @pytest.mark.run(order=39)
    def test_039_Check_DNS_lookup_stopped_on_ipv4_ospf_interface(self):
        """
        Validate BFD Internal DNS monitoring is disabled on OSPF ipv4 interface by checking DNS lookup queries.
        Log Validation
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 39 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Start capturing syslog")
        log("start","/var/log/syslog",config.grid_vip)
        display_msg("Sleeping for 10 seconds")
        sleep(10)
        display_msg("Stop capturing log")
        log("stop","/var/log/syslog",config.grid_vip)
        
        display_msg("Validate captured log for dns lookup queries")
        try:
            logv("\'::1.*query: . IN A - (1111::1111)\'","/var/log/syslog",config.grid_vip)
            logv("\'::1.*UDP: query: . IN A response: REFUSED\'","/var/log/syslog",config.grid_vip)
            display_msg("FAIL: BFD Internal DNS Monitoring is still active.")
            assert False
        except Exception as E:
            if 'returned non-zero exit status 1' in str(E):
                display_msg("PASS: BFD Internal DNS Monitoring is not active.")
            else:
                display_msg(E)
                assert False
        
        display_msg("---------Test Case 39 Execution Completed----------")

    @pytest.mark.run(order=40)
    def test_040_Enable_BFD_Internal_DNS_Monitoring_for_OSPF_ipv4(self):
        """
        Enable BFD Internal DNS Monitoring field and validate no DNS lookup is happening.
        Log Validation
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 40 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Enable BFD Internal DNS Monitoring on ipv4 OSPF interface")
        get_ref = ib_NIOS.wapi_request('GET', object_type='member?_return_fields=ospf_list')
        display_msg(get_ref)
        ref = json.loads(get_ref)[0]['_ref']
        
        old_data = json.loads(get_ref)[0]["ospf_list"]
        to_be_modified = ''
        to_be_kept = ''
        for item in old_data:
            if item['is_ipv4'] == False:
                to_be_modified = item
            elif item['is_ipv4'] == True:
                to_be_kept = item
        if not to_be_modified:
            display_msg("FAIL: Failed to find ipv6 OSPF config")
            assert False
        data={"ospf_list": [{
              "area_id": to_be_modified['area_id'],
              "area_type": to_be_modified['area_type'],
              "authentication_type": to_be_modified['authentication_type'],
              "auto_calc_cost_enabled": to_be_modified['auto_calc_cost_enabled'],
              "cost": to_be_modified['cost'],
              "dead_interval": to_be_modified['dead_interval'],
              "enable_bfd": to_be_modified['enable_bfd'],
              "bfd_template": to_be_modified['bfd_template'],
              "hello_interval": to_be_modified['hello_interval'],
              "interface": to_be_modified['interface'],
              "is_ipv4": to_be_modified['is_ipv4'],
              "key_id": to_be_modified['key_id'],
              "retransmit_interval": to_be_modified['retransmit_interval'],
              "transmit_delay": to_be_modified['transmit_delay'],
              "enable_bfd_dnscheck": True
              }]}
        
        if to_be_kept:
            data["ospf_list"].extend([to_be_kept])
        display_msg("DATA: ")
        display_msg(data, is_dict=True)
        response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(data))
        if type(response) == tuple:
            display_msg(json.loads(response[1])['text'])
            display_msg("FAIL: Failed to update anycast OSPF. Debug above log messages to find the root cause")
            assert False
        else:
            display_msg(response)
            display_msg("PASS: Successfully updated anycast OSPF")
            sleep(120)
        
        display_msg("---------Test Case 40 Execution Completed----------")

    @pytest.mark.run(order=41)
    def test_041_Check_DNS_lookup_on_ipv4_ospf_interface_is_back(self):
        """
        Validate BFD Internal DNS monitoring is disabled on OSPF ipv4 interface by checking DNS lookup queries.
        Log Validation
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 41 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Start capturing syslog")
        log("start","/var/log/syslog",config.grid_vip)
        display_msg("Sleeping for 10 seconds")
        sleep(10)
        display_msg("Stop capturing log")
        log("stop","/var/log/syslog",config.grid_vip)
        
        display_msg("Validate captured log for dns lookup queries")
        try:
            logv("\'::1.*query: . IN A - (1111::1111)\'","/var/log/syslog",config.grid_vip)
            logv("\'::1.*UDP: query: . IN A response: REFUSED\'","/var/log/syslog",config.grid_vip)
            display_msg("PASS: BFD Internal DNS Monitoring is active.")
        except Exception as E:
            if 'returned non-zero exit status 1' in str(E):
                display_msg("FAIL: BFD Internal DNS Monitoring is not yet active.")
                assert False
            else:
                display_msg(E)
                assert False
        
        display_msg("---------Test Case 41 Execution Completed----------")

# Disable BFD Internal DNS Monitoring for BGP IPV4
    @pytest.mark.run(order=42)
    def test_042_Disable_BFD_Internal_DNS_Monitoring_for_BGP_ipv4(self):
        """
        Disable BFD Internal DNS Monitoring field and validate no DNS lookup is happening.
        Log Validation
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 42 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Disable BFD Internal DNS Monitoring on ipv4 BGP interface")
        get_ref = ib_NIOS.wapi_request('GET', object_type='member?_return_fields=bgp_as')
        display_msg(get_ref)
        ref = json.loads(get_ref)[0]['_ref']
        
        from ipaddress import ip_address, IPv4Address, IPv6Address
        
        old_data = json.loads(get_ref)[0]["bgp_as"][0]
        to_be_modified = ''
        to_be_kept = ''
        for item in old_data["neighbors"]:
            if type(ip_address(item["neighbor_ip"])) is IPv4Address:
                to_be_modified = item
            elif type(ip_address(item["neighbor_ip"])) is IPv6Address:
                to_be_kept = item
        if not to_be_modified:
            display_msg("FAIL: Failed to find ipv4 BGP config")
            assert False
        data={"bgp_as": [
        {
            "as": old_data["as"],
            "holddown": old_data["holddown"],
            "keepalive": old_data["keepalive"],
            "link_detect": old_data["link_detect"],
            "neighbors": [
                {
                    "authentication_mode": to_be_modified['authentication_mode'],
                    "enable_bfd": to_be_modified['enable_bfd'],
                    "interface": to_be_modified['interface'],
                    "multihop": to_be_modified['multihop'],
                    "multihop_ttl": to_be_modified['multihop_ttl'],
                    "neighbor_ip": to_be_modified['neighbor_ip'],
                    "remote_as": to_be_modified['remote_as'],
                    "bfd_template": to_be_modified['bfd_template'],
                    "enable_bfd_dnscheck": False
                }
            ]
        }
    ]}
        
        if to_be_kept:
            data["bgp_as"][0]["neighbors"].extend([to_be_kept])
        display_msg("DATA: ")
        display_msg(data, is_dict=True)
        response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(data))
        if type(response) == tuple:
            display_msg(json.loads(response[1])['text'])
            display_msg("FAIL: Failed to update anycast BGP. Debug above log messages to find the root cause")
            assert False
        else:
            display_msg(response)
            display_msg("PASS: Successfully updated anycast BGP")
            sleep(120)
        
        display_msg("---------Test Case 42 Execution Completed----------")

    @pytest.mark.run(order=43)
    def test_043_Check_DNS_lookup_stopped_on_ipv4_BGP_interface(self):
        """
        Validate BFD Internal DNS monitoring is disabled on BGP ipv4 interface by checking DNS lookup queries.
        Log Validation
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 43 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Start capturing syslog")
        log("start","/var/log/syslog",config.grid_vip)
        display_msg("Sleeping for 10 seconds")
        sleep(10)
        display_msg("Stop capturing log")
        log("stop","/var/log/syslog",config.grid_vip)
        
        display_msg("Validate captured log for dns lookup queries")
        try:
            logv("\'127.0.0.1.*query: . IN A - (1.1.1.2)\'","/var/log/syslog",config.grid_vip)
            logv("\'127.0.0.1.*UDP: query: . IN A response: REFUSED\'","/var/log/syslog",config.grid_vip)
            display_msg("FAIL: BFD Internal DNS Monitoring is still active.")
            assert False
        except Exception as E:
            if 'returned non-zero exit status 1' in str(E):
                display_msg("PASS: BFD Internal DNS Monitoring is not active.")
            else:
                display_msg(E)
                assert False
        
        display_msg("---------Test Case 43 Execution Completed----------")

    @pytest.mark.run(order=44)
    def test_044_Enable_BFD_Internal_DNS_Monitoring_for_BGP_ipv4(self):
        """
        Enable BFD Internal DNS Monitoring field and validate no DNS lookup is happening.
        Log Validation
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 44 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Enable BFD Internal DNS Monitoring on ipv4 BGP interface")
        get_ref = ib_NIOS.wapi_request('GET', object_type='member?_return_fields=bgp_as')
        display_msg(get_ref)
        ref = json.loads(get_ref)[0]['_ref']
        
        from ipaddress import ip_address, IPv4Address, IPv6Address
        
        old_data = json.loads(get_ref)[0]["bgp_as"][0]
        to_be_modified = ''
        to_be_kept = ''
        for item in old_data["neighbors"]:
            if type(ip_address(item["neighbor_ip"])) is IPv4Address:
                to_be_modified = item
            elif type(ip_address(item["neighbor_ip"])) is IPv6Address:
                to_be_kept = item
        if not to_be_modified:
            display_msg("FAIL: Failed to find ipv4 BGP config")
            assert False
        data={"bgp_as": [
        {
            "as": old_data["as"],
            "holddown": old_data["holddown"],
            "keepalive": old_data["keepalive"],
            "link_detect": old_data["link_detect"],
            "neighbors": [
                {
                    "authentication_mode": to_be_modified['authentication_mode'],
                    "enable_bfd": to_be_modified['enable_bfd'],
                    "interface": to_be_modified['interface'],
                    "multihop": to_be_modified['multihop'],
                    "multihop_ttl": to_be_modified['multihop_ttl'],
                    "neighbor_ip": to_be_modified['neighbor_ip'],
                    "remote_as": to_be_modified['remote_as'],
                    "bfd_template": to_be_modified['bfd_template'],
                    "enable_bfd_dnscheck": True
                }
            ]
        }
    ]}
        
        if to_be_kept:
            data["bgp_as"][0]["neighbors"].extend([to_be_kept])
        display_msg("DATA: ")
        display_msg(data, is_dict=True)
        response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(data))
        if type(response) == tuple:
            display_msg(json.loads(response[1])['text'])
            display_msg("FAIL: Failed to update anycast BGP. Debug above log messages to find the root cause")
            assert False
        else:
            display_msg(response)
            display_msg("PASS: Successfully updated anycast BGP")
            sleep(120)
        
        display_msg("---------Test Case 44 Execution Completed----------")

    @pytest.mark.run(order=45)
    def test_045_Check_DNS_lookup_on_ipv4_bgp_interface_is_back(self):
        """
        Validate BFD Internal DNS monitoring is disabled on BGP ipv4 interface by checking DNS lookup queries.
        Log Validation
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 45 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Start capturing syslog")
        log("start","/var/log/syslog",config.grid_vip)
        display_msg("Sleeping for 10 seconds")
        sleep(10)
        display_msg("Stop capturing log")
        log("stop","/var/log/syslog",config.grid_vip)
        
        display_msg("Validate captured log for dns lookup queries")
        try:
            logv("\'127.0.0.1.*query: . IN A - (1.1.1.2)\'","/var/log/syslog",config.grid_vip)
            logv("\'127.0.0.1.*UDP: query: . IN A response: REFUSED\'","/var/log/syslog",config.grid_vip)
            display_msg("PASS: BFD Internal DNS Monitoring is active.")
        except Exception as E:
            if 'returned non-zero exit status 1' in str(E):
                display_msg("FAIL: BFD Internal DNS Monitoring is not yet active.")
                assert False
            else:
                display_msg(E)
                assert False
        
        display_msg("---------Test Case 45 Execution Completed----------")

# Disable BFD Internal DNS Monitoring for BGP IPV6
    @pytest.mark.run(order=46)
    def test_046_Disable_BFD_Internal_DNS_Monitoring_for_BGP_ipv6(self):
        """
        Disable BFD Internal DNS Monitoring field and validate no DNS lookup is happening.
        Log Validation
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 38 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Disable BFD Internal DNS Monitoring on ipv6 BGP interface")
        get_ref = ib_NIOS.wapi_request('GET', object_type='member?_return_fields=bgp_as')
        display_msg(get_ref)
        ref = json.loads(get_ref)[0]['_ref']
        
        from ipaddress import ip_address, IPv4Address, IPv6Address
        
        old_data = json.loads(get_ref)[0]["bgp_as"][0]
        to_be_modified = ''
        to_be_kept = ''
        for item in old_data["neighbors"]:
            if type(ip_address(item["neighbor_ip"])) is IPv6Address:
                to_be_modified = item
            elif type(ip_address(item["neighbor_ip"])) is IPv4Address:
                to_be_kept = item
        if not to_be_modified:
            display_msg("FAIL: Failed to find ipv4 BGP config")
            assert False
        data={"bgp_as": [
        {
            "as": old_data["as"],
            "holddown": old_data["holddown"],
            "keepalive": old_data["keepalive"],
            "link_detect": old_data["link_detect"],
            "neighbors": [
                {
                    "authentication_mode": to_be_modified['authentication_mode'],
                    "enable_bfd": to_be_modified['enable_bfd'],
                    "interface": to_be_modified['interface'],
                    "multihop": to_be_modified['multihop'],
                    "multihop_ttl": to_be_modified['multihop_ttl'],
                    "neighbor_ip": to_be_modified['neighbor_ip'],
                    "remote_as": to_be_modified['remote_as'],
                    "bfd_template": to_be_modified['bfd_template'],
                    "enable_bfd_dnscheck": False
                }
            ]
        }
    ]}
        
        if to_be_kept:
            data["bgp_as"][0]["neighbors"].extend([to_be_kept])
        display_msg("DATA: ")
        display_msg(data, is_dict=True)
        response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(data))
        if type(response) == tuple:
            display_msg(json.loads(response[1])['text'])
            display_msg("FAIL: Failed to update anycast BGP. Debug above log messages to find the root cause")
            assert False
        else:
            display_msg(response)
            display_msg("PASS: Successfully updated anycast BGP")
            sleep(120)
        
        display_msg("---------Test Case 46 Execution Completed----------")

    @pytest.mark.run(order=47)
    def test_047_Check_DNS_lookup_stopped_on_ipv4_bgp_interface(self):
        """
        Validate BFD Internal DNS monitoring is disabled on BGP ipv4 interface by checking DNS lookup queries.
        Log Validation
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 47 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Start capturing syslog")
        log("start","/var/log/syslog",config.grid_vip)
        display_msg("Sleeping for 10 seconds")
        sleep(10)
        display_msg("Stop capturing log")
        log("stop","/var/log/syslog",config.grid_vip)
        
        display_msg("Validate captured log for dns lookup queries")
        try:
            logv("\'::1.*query: . IN A - (2222::2222)\'","/var/log/syslog",config.grid_vip)
            logv("\'::1.*UDP: query: . IN A response: REFUSED\'","/var/log/syslog",config.grid_vip)
            display_msg("FAIL: BFD Internal DNS Monitoring is still active.")
            assert False
        except Exception as E:
            if 'returned non-zero exit status 1' in str(E):
                display_msg("PASS: BFD Internal DNS Monitoring is not active.")
            else:
                display_msg(E)
                assert False
        
        display_msg("---------Test Case 47 Execution Completed----------")

    @pytest.mark.run(order=48)
    def test_048_Enable_BFD_Internal_DNS_Monitoring_for_BGP_ipv4(self):
        """
        Enable BFD Internal DNS Monitoring field and validate no DNS lookup is happening.
        Log Validation
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 48 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Enable BFD Internal DNS Monitoring on ipv4 BGP interface")
        get_ref = ib_NIOS.wapi_request('GET', object_type='member?_return_fields=bgp_as')
        display_msg(get_ref)
        ref = json.loads(get_ref)[0]['_ref']
        
        from ipaddress import ip_address, IPv4Address, IPv6Address
        
        old_data = json.loads(get_ref)[0]["bgp_as"][0]
        to_be_modified = ''
        to_be_kept = ''
        for item in old_data["neighbors"]:
            if type(ip_address(item["neighbor_ip"])) is IPv6Address:
                to_be_modified = item
            elif type(ip_address(item["neighbor_ip"])) is IPv4Address:
                to_be_kept = item
        if not to_be_modified:
            display_msg("FAIL: Failed to find ipv4 BGP config")
            assert False
        data={"bgp_as": [
        {
            "as": old_data["as"],
            "holddown": old_data["holddown"],
            "keepalive": old_data["keepalive"],
            "link_detect": old_data["link_detect"],
            "neighbors": [
                {
                    "authentication_mode": to_be_modified['authentication_mode'],
                    "enable_bfd": to_be_modified['enable_bfd'],
                    "interface": to_be_modified['interface'],
                    "multihop": to_be_modified['multihop'],
                    "multihop_ttl": to_be_modified['multihop_ttl'],
                    "neighbor_ip": to_be_modified['neighbor_ip'],
                    "remote_as": to_be_modified['remote_as'],
                    "bfd_template": to_be_modified['bfd_template'],
                    "enable_bfd_dnscheck": True
                }
            ]
        }
    ]}
        
        if to_be_kept:
            data["bgp_as"][0]["neighbors"].extend([to_be_kept])
        display_msg("DATA: ")
        display_msg(data, is_dict=True)
        response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(data))
        if type(response) == tuple:
            display_msg(json.loads(response[1])['text'])
            display_msg("FAIL: Failed to update anycast BGP. Debug above log messages to find the root cause")
            assert False
        else:
            display_msg(response)
            display_msg("PASS: Successfully updated anycast BGP")
            sleep(120)
        
        display_msg("---------Test Case 48 Execution Completed----------")

    @pytest.mark.run(order=49)
    def test_049_Check_DNS_lookup_on_ipv4_bgp_interface_is_back(self):
        """
        Validate BFD Internal DNS monitoring is disabled on BGP ipv4 interface by checking DNS lookup queries.
        Log Validation
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 49 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Start capturing syslog")
        log("start","/var/log/syslog",config.grid_vip)
        display_msg("Sleeping for 10 seconds")
        sleep(10)
        display_msg("Stop capturing log")
        log("stop","/var/log/syslog",config.grid_vip)
        
        display_msg("Validate captured log for dns lookup queries")
        try:
            logv("\'::1.*query: . IN A - (2222::2222)\'","/var/log/syslog",config.grid_vip)
            logv("\'::1.*UDP: query: . IN A response: REFUSED\'","/var/log/syslog",config.grid_vip)
            display_msg("PASS: BFD Internal DNS Monitoring is active.")
        except Exception as E:
            if 'returned non-zero exit status 1' in str(E):
                display_msg("FAIL: BFD Internal DNS Monitoring is not yet active.")
                assert False
            else:
                display_msg(E)
                assert False
        
        display_msg("---------Test Case 49 Execution Completed----------")

##############################################################################################################################
##############################################################################################################################
    @pytest.mark.run(order=50)
    def test_050_configure_anycast_ospf_ipv4_member(self):
        """
        Configure IPV4 Anycast interface with OSPF Config and enable BFD on grid member.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 50 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Delete existing OSPF config on member")
        get_ref = ib_NIOS.wapi_request('GET', object_type='member?_return_fields=ospf_list')
        display_msg(get_ref)
        if json.loads(get_ref)[1]['ospf_list']:
            result = ib_NIOS.wapi_request('PUT', object_type=json.loads(get_ref)[1]['_ref'], fields=json.dumps({'ospf_list':[]}))
            display_msg(result)
            if type(result) == tuple:
                display_msg("FAIL: Failed to delete existing OSPF config on member")
                assert False
        
        display_msg("Add IPV4 OSPF config on member")
        result1 = configure_anycast_ospf(area_id="0.0.0.14",bfd_template='bfdtemp1', fqdn=config.grid_member1_fqdn)
        if not result1:
            assert False
        
        # Validation
        display_msg()
        display_msg("+------------------------------------------+")
        display_msg("|           Validation                     |")
        display_msg("+------------------------------------------+")
        display_msg("Validate added IPV4 OSPF config on member")
        get_ref1 = ib_NIOS.wapi_request('GET', object_type='member?_return_fields=ospf_list')
        display_msg(get_ref1)
        if '0.0.0.14' in get_ref1:
            display_msg("PASS: Successfully validated IPV4 OSPF config on member.")
        else:
            display_msg("FAIL: IPV4 OSPF config is not found on member.")
            assert False
        
        display_msg("Add IPV4 Anycast interface on member")
        result2 = add_anycast_interface('2.2.2.2',connectivity_type='ipv4',ospf=True, fqdn=config.grid_member1_fqdn)
        if not result2:
            assert False
        
        display_msg("Sleeping for 5 minutes")
        sleep(300)
        count = 0
        while not is_grid_alive():
            if count == 5:
                display_msg("Giving up after 5 tries")
                assert False
            display_msg("Sleeping for 1 more minute...")
            sleep(60)
            count += 1
        
        # Validation
        display_msg()
        display_msg("+------------------------------------------+")
        display_msg("|           Validation                     |")
        display_msg("+------------------------------------------+")
        display_msg("Validate added IPV4 Anycast interface on member")
        get_ref2 = ib_NIOS.wapi_request('GET', object_type='member?_return_fields=additional_ip_list')
        display_msg(get_ref2)
        if '2.2.2.2' in get_ref2:
            display_msg("PASS: Successfully validated IPV4 Anycast interface on member.")
        else:
            display_msg("FAIL: IPV4 Anycast interface is not found on member.")
            assert False
        
        display_msg("Add anycast ip address to the listen on list")
        result3 = add_listen_on_ip_addresses('2.2.2.2',fqdn=config.grid_member1_fqdn)
        if not result3:
            assert False
        
        # Validation
        display_msg()
        display_msg("+------------------------------------------+")
        display_msg("|           Validation                     |")
        display_msg("+------------------------------------------+")
        get_ref3 = ib_NIOS.wapi_request('GET', object_type='member:dns?_return_fields=additional_ip_list')
        display_msg(get_ref3)
        if '2.2.2.2' in get_ref3:
            display_msg("PASS: Successfully validated listen on ip adddresses.")
        else:
            display_msg("FAIL: Anycast IP address is not found in the listen on list.")
            assert False
        
        # Update bird config and restart bird process
        display_msg("Update the bird config file and restart bird process")
        result4 = modify_and_restart_bird_process(area_id='0.0.0.14')
        if not result4:
            assert False
        
        display_msg("---------Test Case 50 Execution Completed----------")

    @pytest.mark.run(order=51)
    def test_051_validate_ospf_ipv4_anycast_service(self):
        """
        Dig using anycast IP address and validate anycast service
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 51 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Validate routes are added")
        result1 = validate_routes('2.2.2.2')
        if not result1:
            assert False
        display_msg("Perform dig operation using Anycast interface")
        result2 = validate_anycast_service('2.2.2.2')
        if not result2:
            assert False
        
        display_msg("---------Test Case 51 Execution Completed----------")

    @pytest.mark.run(order=52)
    def test_052_validate_bfd_internal_dns_monitoring_is_enabled_by_default_ospf_ipv4(self):
        """
        Check enable_bfd_dnscheck field is set true by default.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 52 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Check enable_bfd_dnscheck field is set true by default")
        result = ib_NIOS.wapi_request('GET', object_type='member?_return_fields=ospf_list')
        display_msg(result)
        if json.loads(result)[1]['ospf_list'][0]['enable_bfd_dnscheck'] == True:
            display_msg("PASS: enable_bfd_dnscheck field is set to True by default")
        else:
            display_msg("FAIL: enable_bfd_dnscheck field is set to False by default")
            assert False
        
        display_msg("Check BFD is Up and Running")
        result = check_bfd_status(grid=config.grid_member1_vip)
        if not result:
            display_msg("BFD process is not Up or not running")
            assert False
        display_msg("BFD process is Up and Running")
        
        display_msg("---------Test Case 52 Execution Completed----------")

# System related activities
# GMC Promotion

    @pytest.mark.run(order=53)
    def test_053_set_member_as_master_candidate(self):
        """
        Set member as master candidate
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 53 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Set member as master candidate")
        get_ref = ib_NIOS.wapi_request('GET', object_type='member')
        display_msg(get_ref)
        for ref in json.loads(get_ref):
            if config.grid_member1_fqdn in ref['_ref']:
                response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps({"master_candidate":True}))
                if type(response) == tuple:
                    display_msg("FAIL: Setting master candidate")
                    assert False
        restart_services()
        display_msg("PASS: Successfully set as master candidate")
        
        display_msg("Sleep for 5 min for database switchover")
        sleep(300)
        
        # Validation
        get_ref1 = ib_NIOS.wapi_request('GET', object_type='member?_return_fields=master_candidate')
        display_msg(get_ref1)
        for ref1 in json.loads(get_ref1):
            if config.grid_member1_fqdn in ref1['_ref']:
                if ref1['master_candidate'] == True:
                    display_msg("PASS: Master candidate validation")
                else:
                    display_msg("FAIL: Master candidate validation")
                    assert False
        
        display_msg("---------Test Case 53 Execution Completed----------")

    @pytest.mark.run(order=54)
    def test_054_Perform_gmc_promotion(self):
        """
        Perform GMC Promotion on the Master Candidate
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 54 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Perform GMC Promotion")
        args = "sshpass -p 'infoblox' ssh -o StrictHostKeyChecking=no admin@"+config.grid_member1_vip
        args = shlex.split(args)
        child = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        child.stdin.write("set promote_master\n")
        child.stdin.write("n\n")
        child.stdin.write("y\n")
        child.stdin.write("y\n")
        output = child.communicate()
        flag = False
        for line in output:
            display_msg(line)
            if 'Master promotion beginning on this member' in line:
                flag = True
        if flag:
            display_msg("PASS: GMC promotion successfully done")
        else:
            display_msg("FAIL: GMC promotion failed")
            assert False
        
        display_msg("Sleep for 3 minutes")
        sleep(200)
        
        display_msg("---------Test Case 54 Execution Completed----------")

    @pytest.mark.run(order=55)
    def test_055_validate_ospf_ipv4_anycast_service_promted_master(self):
        """
        Dig using anycast IP address and validate anycast service
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 55 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Validate routes are added")
        result1 = validate_routes('2.2.2.2')
        if not result1:
            assert False
        display_msg("Perform dig operation using Anycast interface")
        result2 = validate_anycast_service('2.2.2.2')
        if not result2:
            assert False
        
        display_msg("---------Test Case 55 Execution Completed----------")
    
    @pytest.mark.run(order=56)
    def test_056_validate_bfd_internal_dns_monitoring_is_enabled_by_default_ospf_ipv4_promted_master(self):
        """
        Check enable_bfd_dnscheck field is set true by default.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 56 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Check enable_bfd_dnscheck field is set true by default")
        result = ib_NIOS.wapi_request('GET', object_type='member?_return_fields=ospf_list',grid_vip=config.grid_member1_vip)
        display_msg(result)
        if json.loads(result)[0]['ospf_list'][0]['enable_bfd_dnscheck'] == True:
            display_msg("PASS: enable_bfd_dnscheck field is set to True by default")
        else:
            display_msg("FAIL: enable_bfd_dnscheck field is set to False by default")
            assert False
        
        display_msg("Check BFD is Up and Running")
        result = check_bfd_status(grid=config.grid_member1_vip)
        if not result:
            display_msg("BFD process is not Up or not running")
            assert False
        display_msg("BFD process is Up and Running")
        
        display_msg("---------Test Case 56 Execution Completed----------")
    
    @pytest.mark.run(order=57)
    def test_057_Perform_gmc_promotion_on_old_master(self):
        """
        Perform GMC Promotion on the old Master to make it Master again
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 57 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Perform GMC Promotion on old master")
        args = "sshpass -p 'infoblox' ssh -o StrictHostKeyChecking=no admin@"+config.grid_vip
        args = shlex.split(args)
        child = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        child.stdin.write("set promote_master\n")
        child.stdin.write("n\n")
        child.stdin.write("y\n")
        child.stdin.write("y\n")
        output = child.communicate()
        flag = False
        for line in output:
            display_msg(line)
            if 'Master promotion beginning on this member' in line:
                flag = True
        if flag:
            display_msg("PASS: GMC promotion successfully done")
        else:
            display_msg("FAIL: GMC promotion failed")
            assert False
        
        display_msg("Sleep for 5 minutes for database switchover")
        sleep(300)
        
        # Update bird config and restart bird process
        display_msg("Update the bird config file and restart bird process")
        result4 = modify_and_restart_bird_process(area_id='0.0.0.12')
        if not result4:
            assert False
        
        display_msg("---------Test Case 57 Execution Completed----------")
    
# Restart

    @pytest.mark.run(order=58)
    def test_058_Perform_product_restart(self):
        """
        Perform product restart on the grid
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 58 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Perform product restart")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(config.grid_vip, username='root', password = 'infoblox')
        stdin, stdout, stderr = client.exec_command("/infoblox/rc restart")
        #output = stdout.read()
        client.close()
        #display_msg(output)
        display_msg("Sleep for 2 minutes")
        sleep(120)
        count = 0
        while not is_grid_alive():
            if count == 5:
                display_msg("Giving up after 5 tries")
                assert False
            display_msg("Sleeping for 1 more minute...")
            sleep(60)
            count += 1
        
        display_msg("---------Test Case 58 Execution Completed----------")
    
    @pytest.mark.run(order=59)
    def test_059_validate_ospf_ipv4_anycast_service_after_restart(self):
        """
        Dig using anycast IP address and validate anycast service
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 59 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Validate routes are added")
        result1 = validate_routes('1.1.1.1')
        if not result1:
            assert False
        display_msg("Perform dig operation using Anycast interface")
        result2 = validate_anycast_service('1.1.1.1')
        if not result2:
            assert False
        
        display_msg("---------Test Case 59 Execution Completed----------")
    
    @pytest.mark.run(order=60)
    def test_060_validate_bfd_internal_dns_monitoring_is_enabled_by_default_ospf_ipv4_after_restart(self):
        """
        Check enable_bfd_dnscheck field is set true by default.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 60 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Check enable_bfd_dnscheck field is set true by default")
        result = ib_NIOS.wapi_request('GET', object_type='member?_return_fields=ospf_list')
        display_msg(result)
        if json.loads(result)[0]['ospf_list'][0]['enable_bfd_dnscheck'] == True:
            display_msg("PASS: enable_bfd_dnscheck field is set to True by default")
        else:
            display_msg("FAIL: enable_bfd_dnscheck field is set to False by default")
            assert False
        
        display_msg("Check BFD is Up and Running")
        result = check_bfd_status()
        if not result:
            display_msg("BFD process is not Up or not running")
            assert False
        display_msg("BFD process is Up and Running")
        
        display_msg("---------Test Case 60 Execution Completed----------")

# Reboot

    @pytest.mark.run(order=61)
    def test_061_Perform_reboot_operation(self):
        """
        Perform reboot operation on the grid
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 61 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Perform reboot operation")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(config.grid_vip, username='root', password = 'infoblox')
        stdin, stdout, stderr = client.exec_command("reboot")
        #output = stdout.read()
        #display_msg(output)
        display_msg("Sleep for 15 minutes")
        sleep(900)
        count = 0
        while not is_grid_alive():
            if count == 5:
                display_msg("Giving up after 5 tries")
                assert False
            display_msg("Sleeping for 1 more minute...")
            sleep(60)
            count += 1
        
        display_msg("---------Test Case 61 Execution Completed----------")

    @pytest.mark.run(order=62)
    def test_062_validate_ospf_ipv4_anycast_service_after_reboot(self):
        """
        Dig using anycast IP address and validate anycast service
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 62 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Validate routes are added")
        result1 = validate_routes('1.1.1.1')
        if not result1:
            assert False
        display_msg("Perform dig operation using Anycast interface")
        result2 = validate_anycast_service('1.1.1.1')
        if not result2:
            assert False
        
        display_msg("---------Test Case 62 Execution Completed----------")
    
    @pytest.mark.run(order=63)
    def test_063_validate_bfd_internal_dns_monitoring_is_enabled_by_default_ospf_ipv4_after_reboot(self):
        """
        Check enable_bfd_dnscheck field is set true by default.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 63 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Check enable_bfd_dnscheck field is set true by default")
        result = ib_NIOS.wapi_request('GET', object_type='member?_return_fields=ospf_list'  )
        display_msg(result)
        if json.loads(result)[0]['ospf_list'][0]['enable_bfd_dnscheck'] == True:
            display_msg("PASS: enable_bfd_dnscheck field is set to True by default")
        else:
            display_msg("FAIL: enable_bfd_dnscheck field is set to False by default")
            assert False
        
        display_msg("Check BFD is Up and Running")
        result = check_bfd_status()
        if not result:
            display_msg("BFD process is not Up or not running")
            assert False
        display_msg("BFD process is Up and Running")
        
        display_msg("---------Test Case 63 Execution Completed----------")
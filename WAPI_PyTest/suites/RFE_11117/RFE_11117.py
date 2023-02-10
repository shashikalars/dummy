#!/usr/bin/env python
__author__ = "Chetan Kumar PG"
__email__  = "cpg@infoblox.com"

#############################################################################
#  Grid Set up required:                                                    #
#  1. HA Master + IBFLEX + SA Grid2                                         #
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
logging.basicConfig(format='%(asctime)s - %(name)s(%(process)d) - %(levelname)s - %(message)s',filename="rfe_11117.log" ,level=logging.DEBUG,filemode='w')

def display_msg(x=""):
    """ 
    Additional function.
    """
    logging.info(x)
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

def restart_services(grid=config.grid_vip, service='ALL'):
    """
    Restart Services
    """
    display_msg()
    display_msg("+----------------------------------------------+")
    display_msg("|           Restart Services                   |")
    display_msg("+----------------------------------------------+")
    get_ref =  ib_NIOS.wapi_request('GET', object_type="grid",grid_vip=grid)
    ref = json.loads(get_ref)[0]['_ref']
    data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": service}
    restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices", fields=json.dumps(data),grid_vip=grid)
    sleep(20)

def bfd_template(name='bfdtemp'):
    '''
    Add BFD Template
    '''
    display_msg()
    display_msg("+----------------------------------------------+")
    display_msg("|               Add BFD Template               |")
    display_msg("+----------------------------------------------+")
    display_msg("Adding BFD Template : "+name)
    response = ib_NIOS.wapi_request('POST', object_type='bfdtemplate', fields=json.dumps({"name":name}))
    if type(response) == tuple:
        display_msg(json.loads(response[1])['text'])
        display_msg("FAIL: Failed to add bfd template. Debug above log messages to find the root cause")
        assert False
    else:
        display_msg(response)
        display_msg("PASS: Successfully added bfd template")

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
    display_msg(data)
    response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data))
    if type(response) == tuple:
        display_msg(json.loads(response[1])['text'])
        display_msg("FAIL: Failed to add anycast interface. Debug above log messages to find the root cause")
        assert False
    else:
        display_msg(response)
        display_msg("PASS: Successfully added anycast interface")

def configure_anycast_ospf(area_id="0.0.0.12",fqdn=config.grid_fqdn, auth_type='NONE',is_ipv4=True, auth_key='',key_id=1,bfd_template=''):
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
                "authentication_type": auth_type,
                "auto_calc_cost_enabled": True,
                "cost": 1,
                "dead_interval": 40,
                "enable_bfd": False,
                "hello_interval": 10,
                "interface": "LAN_HA",
                "is_ipv4": is_ipv4,
                "key_id": 1,
                "retransmit_interval": 5,
                "transmit_delay": 1
            }
        ]}
    if auth_type == 'SIMPLE':
        if not auth_key:
            display_msg("FAIL: Provide Authentication Key when Authentication type is not NONE")
            assert False
        data["ospf_list"][0]["authentication_key"] = auth_key
    elif auth_type == 'MESSAGE_DIGEST':
        if not auth_key:
            display_msg("FAIL: Provide Authentication Key when Authentication type is not NONE")
            assert False
        data["ospf_list"][0]["authentication_key"] = auth_key
        data["ospf_list"][0]["key_id"] = key_id
    if bfd_template:
        data["ospf_list"][0]["enable_bfd"] = True
        data["ospf_list"][0]["bfd_template"] = bfd_template

    if old_data:
        if not old_data[0]["is_ipv4"] == data["ospf_list"][0]["is_ipv4"]:
            data["ospf_list"].extend(old_data)
    if not area_id:
        data = {"ospf_list":[]}
    display_msg("DATA: ")
    display_msg(data)
    response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data))
    if type(response) == tuple:
        display_msg(json.loads(response[1])['text'])
        display_msg("FAIL: Failed to configure anycast OSPF. Debug above log messages to find the root cause")
        assert False
    else:
        display_msg(response)
        display_msg("PASS: Successfully configured anycast OSPF")

def configure_anycast_bgp(bgp_as=12,neighbor_ip=config.anycast_client,fqdn=config.grid_fqdn, auth_type='NONE',bgp_neighbor_pass='',bfd_template=''):
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
            "holddown": 16,
            "keepalive": 4,
            "link_detect": False,
            "neighbors": [
                {
                    "authentication_mode": auth_type,
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
    if auth_type == 'MD5':
        if not bgp_neighbor_pass:
            display_msg("FAIL: Provide BGP Neighbor Password when Authentication Mode is not NONE")
            assert False
        data["bgp_as"][0]["neighbors"][0]["bgp_neighbor_pass"] = bgp_neighbor_pass
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
    display_msg(data)
    response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data))
    if type(response) == tuple:
        display_msg(json.loads(response[1])['text'])
        display_msg("FAIL: Failed to configure anycast BGP. Debug above log messages to find the root cause")
        assert False
    else:
        display_msg(response)
        display_msg("PASS: Successfully configured anycast BGP")

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
    display_msg(data)
    response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data))
    if type(response) == tuple:
        display_msg(json.loads(response[1])['text'])
        display_msg("FAIL: Failed to add anycast address to listen on list. Debug above log messages to find the root cause")
        assert False
    else:
        display_msg(response)
        restart_services()
        display_msg("PASS: Successfully added anycast address to listen on list")

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
    client.connect(config.anycast_client, username='root', password = 'infoblox')
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
    
    # Clean the file
    os.system("rm -rf "+file)
    
    # restarting the bird process
    bird = file.split('.')[0]
    stdin, stdout, stderr = client.exec_command("pidof "+bird)
    pid = stdout.read()
    display_msg("PID: "+pid)
    stdin, stdout, stderr = client.exec_command("ps ax | grep bird")
    display_msg(stdout.read())
    if pid:
        stdin, stdout, stderr = client.exec_command("kill -9 "+pid)
        display_msg(stdout.read())
        display_msg(stderr.read())
    stdin, stdout, stderr = client.exec_command(bird+" -c /usr/local/etc/"+file)
    display_msg(stdout.read())
    display_msg(stderr.read())
    display_msg("Sleep for 3 minutes")
    sleep(200)
    
    # validation
    stdin, stdout, stderr = client.exec_command("ps ax | grep bird")
    display_msg(stdout.read())
    stdin, stdout, stderr = client.exec_command("pidof "+bird)
    pid = stdout.read()
    client.close()
    if pid:
        display_msg("Bird process started successfully")
    else:
        display_msg("Bird process not found")
        assert False

def validate_anycast_service(address,record='a.test.com',lookfor='1.1.1.1'):
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
        assert False
    display_msg("PASS: Dig operation succeeded with expected result")
    
def get_anycast_password(protocol,grid=config.grid_vip):
    '''
    Login to grid using root user and get the anycast password from /infoblox/var/quagga/*****.conf files
    Returns anycast password
    '''
    remove_known_hosts_file()
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
    mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
    client.connect(grid, username='root', pkey = mykey)
    display_msg("cat /infoblox/var/quagga/"+protocol+"d.conf")
    stdin, stdout, stderr = client.exec_command("cat /infoblox/var/quagga/"+protocol+"d.conf")
    pasword = ''
    enable_password = ''
    for line in stdout.readlines():
        line = line.encode('ascii','ignore')
        match = re.match("^password (.+)$", line)
        match2 = re.match("^enable password (.+)$", line)
        if match:
            pasword = match.group(1)
            display_msg("Password: "+pasword)
        elif match2:
            enable_password = match2.group(1)
            display_msg("Enable password: "+enable_password)
    client.close()
    return pasword, enable_password

def get_pswd_from_cli(protocol,grid=config.grid_vip,user='admin',password='infoblox'):
    '''
    Execute show ospf/bgp/bfd config CLI and return the password
    '''
    remove_known_hosts_file()
    try:
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no '+user+'@'+grid)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline(password)
        child.expect('Infoblox >')
        child.sendline('show '+protocol+' config')
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
    output=output.split('\n')
    pasword = ''
    enable_password = ''
    for line in output:
        line = line.encode('ascii','ignore')
        match = re.match("^password (.+).*", line)
        match2 = re.match("^enable password (.+)$", line)
        if match:
            pasword = match.group(1)
            display_msg("Password: "+pasword)
        elif match2:
            enable_password = match2.group(1)
            display_msg("Enable password: "+enable_password)
    return pasword, enable_password

def validate_anycast_password(protocol,password,grid=config.grid_vip):
    '''
    Telent using anyacst password and validate the password.
    '''
    remove_known_hosts_file()
    try:
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+grid)
        child.logfile=sys.stdout
        child.expect('#',timeout=None)
        child.sendline('telnet localhost '+protocol+'d')
        child.expect('Password:')
        child.sendline(password)
        child.expect('>')
        child.sendline('enable')
        child.expect('Password:')
        child.sendline(password)
        child.expect('#')
        child.sendline('exit')
        child.sendline('exit')
    except Exception as E:
        display_msg("Exception: ")
        display_msg(E)
        display_msg("FAIL: Anycast password validation failed. Please debug above log to find root cause")
        assert False
    finally:
        child.close()

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
        assert True
    else:
        display_msg("Selecting '"+group+"' for remote user mapping failed")
        assert False


class NIOSSPT_11117(unittest.TestCase):
    
    @pytest.mark.run(order=1)
    def test_001_setup(self):
        """
        setup method: Used for configuring pre-required configs.
        """
        display_msg()
        display_msg("+----------------------------------------------+")
        display_msg("|           Test Case setup Started            |")
        display_msg("+----------------------------------------------+")
        
        display_msg("Add BFD Template")
        bfd_template()
        
        # Validation
        bfd_ref = ib_NIOS.wapi_request('GET', object_type='bfdtemplate', params='?name=bfdtemp')
        display_msg(bfd_ref)
        if 'bfdtemp' in bfd_ref:
            display_msg("PASS: BFD template found")
        else:
            display_msg("FAIL: BFD template not found")
            assert False
        
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
        dns_ref = ib_NIOS.wapi_request('GET', object_type='member:dns?_return_fields=enable_dns')
        display_msg(dns_ref)
        if 'true' in dns_ref:
            display_msg("PASS: DNS service vaidation")
        else:
            display_msg("FAIL: DNS service vaidation")
            assert False
        
        display_msg("---------Test Case setup Execution Completed----------")
    
    @pytest.mark.run(order=2)
    def test_002_add_auth_zone(self):
        """
        Add an authoritative zone.
        """
        display_msg()
        display_msg("+----------------------------------------------+")
        display_msg("|           Test Case 2 Started                |")
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
        get_ref = ib_NIOS.wapi_request('GET',object_type="zone_auth?fqdn=test.com")
        display_msg(get_ref)
        if 'test.com' in get_ref:
            display_msg("PASS: Zone test.com found")
        else:
            display_msg("FAIL: Zone test.com not found")
            assert False
        
        display_msg("---------Test Case 2 Execution Completed----------")

    @pytest.mark.run(order=3)
    def test_003_add_a_record(self):
        """
        Add a record in the test.com zone.
        """
        display_msg()
        display_msg("+----------------------------------------------+")
        display_msg("|           Test Case 3 Started                |")
        display_msg("+----------------------------------------------+")
        
        display_msg("Add a record a.test.com")
        data = {"name":"a.test.com",
                "ipv4addr":"1.1.1.1"
                }
        response = ib_NIOS.wapi_request('POST',object_type='record:a',fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            display_msg("Failure: Add a record a.test.com")
            assert False
        display_msg("PASS: a record a.test.com added")
        
        # Validation
        get_ref = ib_NIOS.wapi_request('GET',object_type="record:a?name=a.test.com")
        display_msg(get_ref)
        if 'a.test.com' in get_ref:
            display_msg("PASS: A record a.test.com found")
        else:
            display_msg("FAIL: A record a.test.com not found")
            assert False
        
        display_msg("---------Test Case 3 Execution Completed----------")

# Anycast OSPF ipv4

    @pytest.mark.run(order=4)
    def test_004_configure_anycast_ospf_ipv4(self):
        """
        Configure IPV4 Anycast interface with OSPF.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 4 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Add OSPF config")
        configure_anycast_ospf(area_id="0.0.0.15",bfd_template='bfdtemp')
        
        # Validation
        display_msg("Validate added OSPF config")
        get_ref1 = ib_NIOS.wapi_request('GET', object_type='member?_return_fields=ospf_list')
        display_msg(get_ref1)
        if '0.0.0.15' in get_ref1:
            display_msg("PASS: Successfully validated OSPF config.")
        else:
            display_msg("FAIL: OSPF config is not found.")
            assert False
        
        display_msg("Add Anycast interface")
        add_anycast_interface('10.1.1.2',ospf=True)
        
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
        display_msg("Validate added Anycast interface")
        get_ref2 = ib_NIOS.wapi_request('GET', object_type='member?_return_fields=additional_ip_list')
        display_msg(get_ref2)
        if '10.1.1.2' in get_ref2:
            display_msg("PASS: Successfully validated Anycast interface.")
        else:
            display_msg("FAIL: Anycast interface is not found.")
            assert False
        
        display_msg("Add anycast ip address to the listen on list")
        add_listen_on_ip_addresses('10.1.1.2')
        
        # Validation
        get_ref3 = ib_NIOS.wapi_request('GET', object_type='member:dns?_return_fields=additional_ip_list')
        display_msg(get_ref3)
        if '10.1.1.2' in get_ref3:
            display_msg("PASS: Successfully validated listen on ip adddresses.")
        else:
            display_msg("FAIL: Anycast IP address is not found in the listen on list.")
            assert False
        
        # Update bird config and restart bird process
        display_msg("Update the bird config file and restart bird process")
        modify_and_restart_bird_process(area_id='0.0.0.15')
        
        display_msg("---------Test Case 4 Execution Completed----------")
        
    @pytest.mark.run(order=5)
    def test_005_validate_ospf_ipv4_anycast_service(self):
        """
        Dig using anycast IP address and validate anycast service
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 5 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Perform dig operation using Anycast interface")
        validate_anycast_service('10.1.1.2')
        
        display_msg("---------Test Case 5 Execution Completed----------")

    @pytest.mark.run(order=6)
    def test_006_validate_anycast_ospf_ipv4_password_encryption(self):
        """
        Validate that the anycast password from the CLI show command is encrypted
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 6 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Getting the actual password from ospfd.conf file")
        password, enable_password = get_anycast_password('ospf')
        if not password or not enable_password:
            display_msg("FAIL: Failed to fetch the password")
            assert False
        
        display_msg("Getting the encrypted password from CLI output")
        pswd, en_pswd = get_pswd_from_cli('ospf')
        if not pswd or not en_pswd:
            display_msg("FAIL: Failed to fetch the password")
            assert False
        
        if password in pswd:
            display_msg("FAIL: CLI output of anycast password is not encrypted")
            assert False
        display_msg("PASS: CLI output of anycast password is encrypted")
        
        if enable_password in en_pswd:
            display_msg("FAIL: CLI output of anycast enable password is not encrypted")
            assert False
        display_msg("PASS: CLI output of anycast enable password is encrypted")
        
        validate_anycast_password('ospf',password)
        display_msg("PASS: Anycast password successfully validated")
        
        validate_anycast_password('ospf',enable_password)
        display_msg("PASS: Anycast enable password successfully validated")
        
        display_msg("---------Test Case 6 Execution Completed----------")


# Anycast OSPF ipv6

    @pytest.mark.run(order=7)
    def test_007_configure_anycast_ospf_ipv6(self):
        """
        Configure IPV6 Anycast interface with OSPF.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 7 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Add IPV6 OSPF config")
        configure_anycast_ospf(area_id="0.0.0.17",bfd_template='bfdtemp',is_ipv4=False)
        
        # Validation
        display_msg("Validate added IPV6 OSPF config")
        get_ref1 = ib_NIOS.wapi_request('GET', object_type='member?_return_fields=ospf_list')
        display_msg(get_ref1)
        if '0.0.0.17' in get_ref1:
            display_msg("PASS: Successfully validated IPV6 OSPF config.")
        else:
            display_msg("FAIL: IPV6 OSPF config is not found.")
            assert False
        
        display_msg("Add IPV6 Anycast interface")
        add_anycast_interface('1111::1111',connectivity_type='ipv6',ospf=True)        
        
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
        display_msg("Validate added IPV6 Anycast interface")
        get_ref2 = ib_NIOS.wapi_request('GET', object_type='member?_return_fields=additional_ip_list')
        display_msg(get_ref2)
        if '1111::1111' in get_ref2:
            display_msg("PASS: Successfully validated IPV6 Anycast interface.")
        else:
            display_msg("FAIL: IPV6 Anycast interface is not found.")
            assert False
        
        display_msg("Add anycast ip address to the listen on list")
        add_listen_on_ip_addresses('1111::1111')
        
        # Validation
        get_ref3 = ib_NIOS.wapi_request('GET', object_type='member:dns?_return_fields=additional_ip_list')
        display_msg(get_ref3)
        if '1111::1111' in get_ref3:
            display_msg("PASS: Successfully validated listen on ip adddresses.")
        else:
            display_msg("FAIL: Anycast IP address is not found in the listen on list.")
            assert False
        
        # Update bird config and restart bird process
        display_msg("Update the bird config file and restart bird process")
        modify_and_restart_bird_process(connectivity_type='ipv6',area_id='0.0.0.17',bgp_neighbor=config.grid_vip_v6,anycast_client=config.anycast_client_v6)
        
        display_msg("---------Test Case 7 Execution Completed----------")
        
    @pytest.mark.run(order=8)
    def test_008_validate_ospf_ipv6_anycast_service(self):
        """
        Dig using anycast IP address and validate anycast service
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 8 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Perform dig operation using IPV6 Anycast interface")
        validate_anycast_service('1111::1111')
        
        display_msg("---------Test Case 8 Execution Completed----------")

    @pytest.mark.run(order=9)
    def test_009_validate_anycast_ospf_ipv6_password_encryption(self):
        """
        Validate that the anycast password from the CLI show command is encrypted
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 9 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Getting the actual password from ospf6d.conf file")
        password, enable_password = get_anycast_password('ospf6')
        if not password or not enable_password:
            display_msg("FAIL: Failed to fetch the password")
            assert False
        
        display_msg("Getting the encrypted password from CLI output")
        pswd, en_pswd = get_pswd_from_cli('ipv6_ospf')
        if not pswd or not en_pswd:
            display_msg("FAIL: Failed to fetch the password")
            assert False
        
        if password in pswd:
            display_msg("FAIL: CLI output of anycast password is not encrypted")
            assert False
        display_msg("PASS: CLI output of anycast password is encrypted")
        
        if enable_password in en_pswd:
            display_msg("FAIL: CLI output of anycast enable password is not encrypted")
            assert False
        display_msg("PASS: CLI output of anycast enable password is encrypted")
        
        validate_anycast_password('ospf6',password)
        display_msg("PASS: Anycast password successfully validated")
        
        validate_anycast_password('ospf6',enable_password)
        display_msg("PASS: Anycast enable password successfully validated")
        
        display_msg("---------Test Case 9 Execution Completed----------")

# Anycast BGP ipv4

    @pytest.mark.run(order=10)
    def test_010_configure_anycast_bgp_ipv4(self):
        """
        Configure IPV4 Anycast interface with BGP.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 10 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Add BGP config")
        configure_anycast_bgp(bgp_as=12,bfd_template='bfdtemp')
        
        # Validation
        display_msg("Validate added BGP config")
        get_ref1 = ib_NIOS.wapi_request('GET', object_type='member?_return_fields=bgp_as')
        display_msg(get_ref1)
        if '12' in get_ref1 and config.anycast_client in get_ref1:
            display_msg("PASS: Successfully validated BGP config.")
        else:
            display_msg("FAIL: BGP config is not found.")
            assert False
        
        display_msg("Add Anycast interface")
        add_anycast_interface('10.1.1.3',bgp=True)
        
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
        display_msg("Validate added Anycast interface")
        get_ref2 = ib_NIOS.wapi_request('GET', object_type='member?_return_fields=additional_ip_list')
        display_msg(get_ref2)
        if '10.1.1.3' in get_ref2:
            display_msg("PASS: Successfully validated Anycast interface.")
        else:
            display_msg("FAIL: Anycast interface is not found.")
            assert False
        
        display_msg("Add anycast ip address to the listen on list")
        add_listen_on_ip_addresses('10.1.1.3')
        
        # Validation
        get_ref3 = ib_NIOS.wapi_request('GET', object_type='member:dns?_return_fields=additional_ip_list')
        display_msg(get_ref3)
        if '10.1.1.3' in get_ref3:
            display_msg("PASS: Successfully validated listen on ip adddresses.")
        else:
            display_msg("FAIL: Anycast IP address is not found in the listen on list.")
            assert False
        
        # Update bird config and restart bird process
        display_msg("Update the bird config file and restart bird process")
        modify_and_restart_bird_process(bgp_as='12')
        
        display_msg("---------Test Case 10 Execution Completed----------")
        
    @pytest.mark.run(order=11)
    def test_011_validate_bgp_ipv4_anycast_service(self):
        """
        Dig using anycast IP address and validate anycast service
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 11 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Perform dig operation using Anycast interface")
        validate_anycast_service('10.1.1.3')
        
        display_msg("---------Test Case 11 Execution Completed----------")

    @pytest.mark.run(order=12)
    def test_012_validate_anycast_bgp_ipv4_password_encryption(self):
        """
        Validate that the anycast password from the CLI show command is encrypted
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 12 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Getting the actual password from bgpd.conf file")
        password, enable_password = get_anycast_password('bgp')
        if not password or not enable_password:
            display_msg("FAIL: Failed to fetch the password")
            assert False
        
        display_msg("Getting the encrypted password from CLI output")
        pswd, en_pswd = get_pswd_from_cli('bgp')
        if not pswd or not en_pswd:
            display_msg("FAIL: Failed to fetch the password")
            assert False
        
        if password in pswd:
            display_msg("FAIL: CLI output of anycast password is not encrypted")
            assert False
        display_msg("PASS: CLI output of anycast password is encrypted")
        
        if enable_password in en_pswd:
            display_msg("FAIL: CLI output of anycast enable password is not encrypted")
            assert False
        display_msg("PASS: CLI output of anycast enable password is encrypted")
        
        validate_anycast_password('bgp',password)
        display_msg("PASS: Anycast password successfully validated")
        
        validate_anycast_password('bgp',enable_password)
        display_msg("PASS: Anycast enable password successfully validated")
        
        display_msg("---------Test Case 12 Execution Completed----------")

# Anycast BGP ipv6

    @pytest.mark.run(order=13)
    def test_013_configure_anycast_bgp_ipv6(self):
        """
        Configure IPV6 Anycast interface with BGP.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 13 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Add IPV6 BGP config")
        configure_anycast_bgp(bgp_as=12,bfd_template='bfdtemp',neighbor_ip=config.anycast_client_v6)
        
        # Validation
        display_msg("Validate added IPV6 BGP config")
        get_ref1 = ib_NIOS.wapi_request('GET', object_type='member?_return_fields=bgp_as')
        display_msg(get_ref1)
        if '12' in get_ref1 and config.anycast_client_v6 in get_ref1:
            display_msg("PASS: Successfully validated IPV6 BGP config.")
        else:
            display_msg("FAIL: IPV6 BGP config is not found.")
            assert False
        
        display_msg("Add IPV6 Anycast interface")
        add_anycast_interface('2222::2222',bgp=True,connectivity_type='ipv6')
        
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
        display_msg("Validate added IPV6 Anycast interface")
        get_ref2 = ib_NIOS.wapi_request('GET', object_type='member?_return_fields=additional_ip_list')
        display_msg(get_ref2)
        if '2222::2222' in get_ref2:
            display_msg("PASS: Successfully validated IPV6 Anycast interface.")
        else:
            display_msg("FAIL: IPV6 Anycast interface is not found.")
            assert False
        
        display_msg("Add IPV6 anycast ip address to the listen on list")
        add_listen_on_ip_addresses('2222::2222')
        
        # Validation
        get_ref3 = ib_NIOS.wapi_request('GET', object_type='member:dns?_return_fields=additional_ip_list')
        display_msg(get_ref3)
        if '2222::2222' in get_ref3:
            display_msg("PASS: Successfully validated listen on ip adddresses.")
        else:
            display_msg("FAIL: IPV6 Anycast IP address is not found in the listen on list.")
            assert False
        
        # Update bird config and restart bird process
        display_msg("Update the bird config file and restart bird process")
        modify_and_restart_bird_process(bgp_as='12',connectivity_type='ipv6',bgp_neighbor=config.grid_vip_v6,anycast_client=config.anycast_client_v6)
        
        display_msg("---------Test Case 13 Execution Completed----------")
        
    @pytest.mark.run(order=14)
    def test_014_validate_bgp_ipv6_anycast_service(self):
        """
        Dig using anycast IP address and validate anycast service
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 14 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Perform dig operation using Anycast interface")
        validate_anycast_service('2222::2222')
        
        display_msg("---------Test Case 14 Execution Completed----------")

    @pytest.mark.run(order=15)
    def test_015_validate_anycast_bgp_ipv6_password_encryption(self):
        """
        Validate that the anycast password from the CLI show command is encrypted
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 15 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Getting the actual password from bgpd.conf file")
        password, enable_password = get_anycast_password('bgp')
        if not password or not enable_password:
            display_msg("FAIL: Failed to fetch the password")
            assert False
        
        display_msg("Getting the encrypted password from CLI output")
        pswd, en_pswd = get_pswd_from_cli('ipv6_bgp')
        if not pswd or not en_pswd:
            display_msg("FAIL: Failed to fetch the password")
            assert False
        
        if password in pswd:
            display_msg("FAIL: CLI output of anycast password is not encrypted")
            assert False
        display_msg("PASS: CLI output of anycast password is encrypted")
        
        if enable_password in en_pswd:
            display_msg("FAIL: CLI output of anycast enable password is not encrypted")
            assert False
        display_msg("PASS: CLI output of anycast enable password is encrypted")
        
        validate_anycast_password('bgp',password)
        display_msg("PASS: Anycast password successfully validated")
        
        validate_anycast_password('bgp',enable_password)
        display_msg("PASS: Anycast enable password successfully validated")

        display_msg("---------Test Case 15 Execution Completed----------")

##############################################################################################################################
# Testing anycast functionality on grid member
# Anycast OSPF ipv4

    @pytest.mark.run(order=16)
    def test_016_configure_anycast_ospf_ipv4_member(self):
        """
        Configure IPV4 Anycast interface with OSPF.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 16 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Add OSPF config")
        configure_anycast_ospf(area_id="0.0.0.25",bfd_template='bfdtemp',fqdn=config.grid_member1_fqdn)
        
        # Validation
        display_msg("Validate added OSPF config")
        get_ref1 = ib_NIOS.wapi_request('GET', object_type='member?_return_fields=ospf_list')
        display_msg(get_ref1)
        if '0.0.0.25' in get_ref1:
            display_msg("PASS: Successfully validated OSPF config.")
        else:
            display_msg("FAIL: OSPF config is not found.")
            assert False
        
        display_msg("Add Anycast interface")
        add_anycast_interface('11.1.1.2',ospf=True,fqdn=config.grid_member1_fqdn)
        
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
        display_msg("Validate added Anycast interface")
        get_ref2 = ib_NIOS.wapi_request('GET', object_type='member?_return_fields=additional_ip_list')
        display_msg(get_ref2)
        if '11.1.1.2' in get_ref2:
            display_msg("PASS: Successfully validated Anycast interface.")
        else:
            display_msg("FAIL: Anycast interface is not found.")
            assert False
        
        display_msg("Add anycast ip address to the listen on list")
        add_listen_on_ip_addresses('11.1.1.2',fqdn=config.grid_member1_fqdn)
        
        # Validation
        get_ref3 = ib_NIOS.wapi_request('GET', object_type='member:dns?_return_fields=additional_ip_list')
        display_msg(get_ref3)
        if '11.1.1.2' in get_ref3:
            display_msg("PASS: Successfully validated listen on ip adddresses.")
        else:
            display_msg("FAIL: Anycast IP address is not found in the listen on list.")
            assert False
        
        # Update bird config and restart bird process
        display_msg("Update the bird config file and restart bird process")
        modify_and_restart_bird_process(area_id='0.0.0.25')
        
        display_msg("---------Test Case 16 Execution Completed----------")
        
    @pytest.mark.run(order=17)
    def test_017_validate_ospf_ipv4_anycast_service_member(self):
        """
        Dig using anycast IP address and validate anycast service
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 17 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Perform dig operation using Anycast interface")
        validate_anycast_service('11.1.1.2')
        
        display_msg("---------Test Case 17 Execution Completed----------")

    @pytest.mark.run(order=18)
    def test_018_validate_anycast_ospf_ipv4_password_encryption_member(self):
        """
        Validate that the anycast password from the CLI show command is encrypted
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 18 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Getting the actual password from ospfd.conf file")
        password, enable_password = get_anycast_password('ospf')
        if not password or not enable_password:
            display_msg("FAIL: Failed to fetch the password")
            assert False
        
        display_msg("Getting the encrypted password from CLI output")
        pswd, en_pswd = get_pswd_from_cli('ospf')
        if not pswd or not en_pswd:
            display_msg("FAIL: Failed to fetch the password")
            assert False
        
        if password in pswd:
            display_msg("FAIL: CLI output of anycast password is not encrypted")
            assert False
        display_msg("PASS: CLI output of anycast password is encrypted")
        
        if enable_password in en_pswd:
            display_msg("FAIL: CLI output of anycast enable password is not encrypted")
            assert False
        display_msg("PASS: CLI output of anycast enable password is encrypted")
        
        validate_anycast_password('ospf',password)
        display_msg("PASS: Anycast password successfully validated")
        
        validate_anycast_password('ospf',enable_password)
        display_msg("PASS: Anycast enable password successfully validated")
        
        display_msg("---------Test Case 18 Execution Completed----------")


# Anycast OSPF ipv6

    @pytest.mark.run(order=19)
    def test_019_configure_anycast_ospf_ipv6_member(self):
        """
        Configure IPV6 Anycast interface with OSPF.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 19 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Add IPV6 OSPF config")
        configure_anycast_ospf(area_id="0.0.0.27",bfd_template='bfdtemp',is_ipv4=False,fqdn=config.grid_member1_fqdn)
        
        # Validation
        display_msg("Validate added IPV6 OSPF config")
        get_ref1 = ib_NIOS.wapi_request('GET', object_type='member?_return_fields=ospf_list')
        display_msg(get_ref1)
        if '0.0.0.27' in get_ref1:
            display_msg("PASS: Successfully validated IPV6 OSPF config.")
        else:
            display_msg("FAIL: IPV6 OSPF config is not found.")
            assert False
        
        display_msg("Add IPV6 Anycast interface")
        add_anycast_interface('1111::2222',connectivity_type='ipv6',ospf=True,fqdn=config.grid_member1_fqdn)        
        
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
        display_msg("Validate added IPV6 Anycast interface")
        get_ref2 = ib_NIOS.wapi_request('GET', object_type='member?_return_fields=additional_ip_list')
        display_msg(get_ref2)
        if '1111::2222' in get_ref2:
            display_msg("PASS: Successfully validated IPV6 Anycast interface.")
        else:
            display_msg("FAIL: IPV6 Anycast interface is not found.")
            assert False
        
        display_msg("Add anycast ip address to the listen on list")
        add_listen_on_ip_addresses('1111::2222',fqdn=config.grid_member1_fqdn)
        
        # Validation
        get_ref3 = ib_NIOS.wapi_request('GET', object_type='member:dns?_return_fields=additional_ip_list')
        display_msg(get_ref3)
        if '1111::2222' in get_ref3:
            display_msg("PASS: Successfully validated listen on ip adddresses.")
        else:
            display_msg("FAIL: Anycast IP address is not found in the listen on list.")
            assert False
        
        # Update bird config and restart bird process
        display_msg("Update the bird config file and restart bird process")
        modify_and_restart_bird_process(connectivity_type='ipv6',area_id='0.0.0.27',bgp_neighbor=config.grid_member1_vip_v6,anycast_client=config.anycast_client_v6)
        
        display_msg("---------Test Case 19 Execution Completed----------")
        
    @pytest.mark.run(order=20)
    def test_020_validate_ospf_ipv6_anycast_service_member(self):
        """
        Dig using anycast IP address and validate anycast service
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 20 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Perform dig operation using IPV6 Anycast interface")
        validate_anycast_service('1111::2222')
        
        display_msg("---------Test Case 20 Execution Completed----------")

    @pytest.mark.run(order=21)
    def test_021_validate_anycast_ospf_ipv6_password_encryption_member(self):
        """
        Validate that the anycast password from the CLI show command is encrypted
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 21 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Getting the actual password from ospf6d.conf file")
        password, enable_password = get_anycast_password('ospf6')
        if not password or not enable_password:
            display_msg("FAIL: Failed to fetch the password")
            assert False
        
        display_msg("Getting the encrypted password from CLI output")
        pswd, en_pswd = get_pswd_from_cli('ipv6_ospf')
        if not pswd or not en_pswd:
            display_msg("FAIL: Failed to fetch the password")
            assert False
        
        if password in pswd:
            display_msg("FAIL: CLI output of anycast password is not encrypted")
            assert False
        display_msg("PASS: CLI output of anycast password is encrypted")
        
        if enable_password in en_pswd:
            display_msg("FAIL: CLI output of anycast enable password is not encrypted")
            assert False
        display_msg("PASS: CLI output of anycast enable password is encrypted")
        
        validate_anycast_password('ospf6',password)
        display_msg("PASS: Anycast password successfully validated")
        
        validate_anycast_password('ospf6',enable_password)
        display_msg("PASS: Anycast enable password successfully validated")
        
        display_msg("---------Test Case 21 Execution Completed----------")

# Anycast BGP ipv4

    @pytest.mark.run(order=22)
    def test_022_configure_anycast_bgp_ipv4_member(self):
        """
        Configure IPV4 Anycast interface with BGP.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 22 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Add BGP config")
        configure_anycast_bgp(bgp_as=22,bfd_template='bfdtemp',fqdn=config.grid_member1_fqdn)
        
        # Validation
        display_msg("Validate added BGP config")
        get_ref1 = ib_NIOS.wapi_request('GET', object_type='member?_return_fields=bgp_as')
        display_msg(get_ref1)
        if '22' in get_ref1 and config.anycast_client in get_ref1:
            display_msg("PASS: Successfully validated BGP config.")
        else:
            display_msg("FAIL: BGP config is not found.")
            assert False
        
        display_msg("Add Anycast interface")
        add_anycast_interface('11.1.1.3',bgp=True,fqdn=config.grid_member1_fqdn)
        
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
        display_msg("Validate added Anycast interface")
        get_ref2 = ib_NIOS.wapi_request('GET', object_type='member?_return_fields=additional_ip_list')
        display_msg(get_ref2)
        if '11.1.1.3' in get_ref2:
            display_msg("PASS: Successfully validated Anycast interface.")
        else:
            display_msg("FAIL: Anycast interface is not found.")
            assert False
        
        display_msg("Add anycast ip address to the listen on list")
        add_listen_on_ip_addresses('11.1.1.3',fqdn=config.grid_member1_fqdn)
        
        # Validation
        get_ref3 = ib_NIOS.wapi_request('GET', object_type='member:dns?_return_fields=additional_ip_list')
        display_msg(get_ref3)
        if '11.1.1.3' in get_ref3:
            display_msg("PASS: Successfully validated listen on ip adddresses.")
        else:
            display_msg("FAIL: Anycast IP address is not found in the listen on list.")
            assert False
        
        # Update bird config and restart bird process
        display_msg("Update the bird config file and restart bird process")
        modify_and_restart_bird_process(bgp_as='22',bgp_neighbor=config.grid_member1_vip)
        
        display_msg("---------Test Case 22 Execution Completed----------")
        
    @pytest.mark.run(order=23)
    def test_023_validate_bgp_ipv4_anycast_service_member(self):
        """
        Dig using anycast IP address and validate anycast service
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 23 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Perform dig operation using Anycast interface")
        validate_anycast_service('11.1.1.3')
        
        display_msg("---------Test Case 23 Execution Completed----------")

    @pytest.mark.run(order=24)
    def test_024_validate_anycast_bgp_ipv4_password_encryption_member(self):
        """
        Validate that the anycast password from the CLI show command is encrypted
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 24 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Getting the actual password from bgpd.conf file")
        password, enable_password = get_anycast_password('bgp')
        if not password or not enable_password:
            display_msg("FAIL: Failed to fetch the password")
            assert False
        
        display_msg("Getting the encrypted password from CLI output")
        pswd, en_pswd = get_pswd_from_cli('bgp')
        if not pswd or not en_pswd:
            display_msg("FAIL: Failed to fetch the password")
            assert False
        
        if password in pswd:
            display_msg("FAIL: CLI output of anycast password is not encrypted")
            assert False
        display_msg("PASS: CLI output of anycast password is encrypted")
        
        if enable_password in en_pswd:
            display_msg("FAIL: CLI output of anycast enable password is not encrypted")
            assert False
        display_msg("PASS: CLI output of anycast enable password is encrypted")
        
        validate_anycast_password('bgp',password)
        display_msg("PASS: Anycast password successfully validated")
        
        validate_anycast_password('bgp',enable_password)
        display_msg("PASS: Anycast enable password successfully validated")
        
        display_msg("---------Test Case 24 Execution Completed----------")

# Anycast BGP ipv6

    @pytest.mark.run(order=25)
    def test_025_configure_anycast_bgp_ipv6_member(self):
        """
        Configure IPV6 Anycast interface with BGP.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 25 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Add IPV6 BGP config")
        configure_anycast_bgp(bgp_as=22,bfd_template='bfdtemp',neighbor_ip=config.anycast_client_v6,fqdn=config.grid_member1_fqdn)
        
        # Validation
        display_msg("Validate added IPV6 BGP config")
        get_ref1 = ib_NIOS.wapi_request('GET', object_type='member?_return_fields=bgp_as')
        display_msg(get_ref1)
        if '22' in get_ref1 and config.anycast_client_v6 in get_ref1:
            display_msg("PASS: Successfully validated IPV6 BGP config.")
        else:
            display_msg("FAIL: IPV6 BGP config is not found.")
            assert False
        
        display_msg("Add IPV6 Anycast interface")
        add_anycast_interface('2222::1111',bgp=True,connectivity_type='ipv6',fqdn=config.grid_member1_fqdn)
        
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
        display_msg("Validate added IPV6 Anycast interface")
        get_ref2 = ib_NIOS.wapi_request('GET', object_type='member?_return_fields=additional_ip_list')
        display_msg(get_ref2)
        if '2222::1111' in get_ref2:
            display_msg("PASS: Successfully validated IPV6 Anycast interface.")
        else:
            display_msg("FAIL: IPV6 Anycast interface is not found.")
            assert False
        
        display_msg("Add IPV6 anycast ip address to the listen on list")
        add_listen_on_ip_addresses('2222::1111',fqdn=config.grid_member1_fqdn)
        
        # Validation
        get_ref3 = ib_NIOS.wapi_request('GET', object_type='member:dns?_return_fields=additional_ip_list')
        display_msg(get_ref3)
        if '2222::1111' in get_ref3:
            display_msg("PASS: Successfully validated listen on ip adddresses.")
        else:
            display_msg("FAIL: IPV6 Anycast IP address is not found in the listen on list.")
            assert False
        
        # Update bird config and restart bird process
        display_msg("Update the bird config file and restart bird process")
        modify_and_restart_bird_process(bgp_as='22',connectivity_type='ipv6',bgp_neighbor=config.grid_member1_vip_v6,anycast_client=config.anycast_client_v6)
        
        display_msg("---------Test Case 25 Execution Completed----------")
        
    @pytest.mark.run(order=26)
    def test_026_validate_bgp_ipv6_anycast_service_member(self):
        """
        Dig using anycast IP address and validate anycast service
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 26 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Perform dig operation using Anycast interface")
        validate_anycast_service('2222::1111')
        
        display_msg("---------Test Case 26 Execution Completed----------")

    @pytest.mark.run(order=27)
    def test_027_validate_anycast_bgp_ipv6_password_encryption_member(self):
        """
        Validate that the anycast password from the CLI show command is encrypted
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 27 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Getting the actual password from bgpd.conf file")
        password, enable_password = get_anycast_password('bgp')
        if not password or not enable_password:
            display_msg("FAIL: Failed to fetch the password")
            assert False
        
        display_msg("Getting the encrypted password from CLI output")
        pswd, en_pswd = get_pswd_from_cli('ipv6_bgp')
        if not pswd or not en_pswd:
            display_msg("FAIL: Failed to fetch the password")
            assert False
        
        if password in pswd:
            display_msg("FAIL: CLI output of anycast password is not encrypted")
            assert False
        display_msg("PASS: CLI output of anycast password is encrypted")
        
        if enable_password in en_pswd:
            display_msg("FAIL: CLI output of anycast enable password is not encrypted")
            assert False
        display_msg("PASS: CLI output of anycast enable password is encrypted")
        
        validate_anycast_password('bgp',password)
        display_msg("PASS: Anycast password successfully validated")
        
        validate_anycast_password('bgp',enable_password)
        display_msg("PASS: Anycast enable password successfully validated")
        
        display_msg("---------Test Case 27 Execution Completed----------")

##############################################################################################################################
# System related activities

# Restart

    @pytest.mark.run(order=28)
    def test_028_Perform_product_restart(self):
        """
        Perform product restart on the grid
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 28 Execution Started           |")
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
        
        display_msg("---------Test Case 28 Execution Completed----------")

    @pytest.mark.run(order=29)
    def test_029_validate_anycast_ospf_ipv4_password_encryption_after_restart(self):
        """
        Validate that the anycast password from the CLI show command is encrypted after restart operation
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 29 Execution Started          |")
        display_msg("----------------------------------------------------")
        display_msg("Getting the actual password from ospfd.conf file")
        password, enable_password = get_anycast_password('ospf')
        if not password or not enable_password:
            display_msg("FAIL: Failed to fetch the password")
            assert False
        
        display_msg("Getting the encrypted password from CLI output")
        pswd, en_pswd = get_pswd_from_cli('ospf')
        if not pswd or not en_pswd:
            display_msg("FAIL: Failed to fetch the password")
            assert False
        
        if password in pswd:
            display_msg("FAIL: CLI output of anycast password is not encrypted")
            assert False
        display_msg("PASS: CLI output of anycast password is encrypted")
        
        if enable_password in en_pswd:
            display_msg("FAIL: CLI output of anycast enable password is not encrypted")
            assert False
        display_msg("PASS: CLI output of anycast enable password is encrypted")
        
        validate_anycast_password('ospf',password)
        display_msg("PASS: Anycast password successfully validated")
        
        validate_anycast_password('ospf',enable_password)
        display_msg("PASS: Anycast enable password successfully validated")
        
        display_msg("---------Test Case 29 Execution Completed----------")


    @pytest.mark.run(order=30)
    def test_030_validate_anycast_ospf_ipv6_password_encryption_after_restart(self):
        """
        Validate that the anycast password from the CLI show command is encrypted after restart operation
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 30 Execution Started          |")
        display_msg("----------------------------------------------------")
        display_msg("Getting the actual password from ospf6d.conf file")
        password, enable_password = get_anycast_password('ospf6')
        if not password or not enable_password:
            display_msg("FAIL: Failed to fetch the password")
            assert False
        
        display_msg("Getting the encrypted password from CLI output")
        pswd, en_pswd = get_pswd_from_cli('ipv6_ospf')
        if not pswd or not en_pswd:
            display_msg("FAIL: Failed to fetch the password")
            assert False
        
        if password in pswd:
            display_msg("FAIL: CLI output of anycast password is not encrypted")
            assert False
        display_msg("PASS: CLI output of anycast password is encrypted")
        
        if enable_password in en_pswd:
            display_msg("FAIL: CLI output of anycast enable password is not encrypted")
            assert False
        display_msg("PASS: CLI output of anycast enable password is encrypted")
        
        validate_anycast_password('ospf6',password)
        display_msg("PASS: Anycast password successfully validated")
        
        validate_anycast_password('ospf6',enable_password)
        display_msg("PASS: Anycast enable password successfully validated")
        
        display_msg("---------Test Case 30 Execution Completed----------")

    @pytest.mark.run(order=31)
    def test_031_validate_anycast_bgp_ipv4_password_encryption_after_restart(self):
        """
        Validate that the anycast password from the CLI show command is encrypted after restart operation
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 31 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Getting the actual password from bgpd.conf file")
        password, enable_password = get_anycast_password('bgp')
        if not password or not enable_password:
            display_msg("FAIL: Failed to fetch the password")
            assert False
        
        display_msg("Getting the encrypted password from CLI output")
        pswd, en_pswd = get_pswd_from_cli('bgp')
        if not pswd or not en_pswd:
            display_msg("FAIL: Failed to fetch the password")
            assert False
        
        if password in pswd:
            display_msg("FAIL: CLI output of anycast password is not encrypted")
            assert False
        display_msg("PASS: CLI output of anycast password is encrypted")
        
        if enable_password in en_pswd:
            display_msg("FAIL: CLI output of anycast enable password is not encrypted")
            assert False
        display_msg("PASS: CLI output of anycast enable password is encrypted")
        
        validate_anycast_password('bgp',password)
        display_msg("PASS: Anycast password successfully validated")
        
        validate_anycast_password('bgp',enable_password)
        display_msg("PASS: Anycast enable password successfully validated")
        
        display_msg("---------Test Case 31 Execution Completed----------")


    @pytest.mark.run(order=32)
    def test_032_validate_anycast_bgp_ipv6_password_encryption_after_restart(self):
        """
        Validate that the anycast password from the CLI show command is encrypted after restart operation
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 32 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Getting the actual password from bgpd.conf file")
        password, enable_password = get_anycast_password('bgp')
        if not password or not enable_password:
            display_msg("FAIL: Failed to fetch the password")
            assert False
        
        display_msg("Getting the encrypted password from CLI output")
        pswd, en_pswd = get_pswd_from_cli('ipv6_bgp')
        if not pswd or not en_pswd:
            display_msg("FAIL: Failed to fetch the password")
            assert False
        
        if password in pswd:
            display_msg("FAIL: CLI output of anycast password is not encrypted")
            assert False
        display_msg("PASS: CLI output of anycast password is encrypted")
        
        if enable_password in en_pswd:
            display_msg("FAIL: CLI output of anycast enable password is not encrypted")
            assert False
        display_msg("PASS: CLI output of anycast enable password is encrypted")
        
        validate_anycast_password('bgp',password)
        display_msg("PASS: Anycast password successfully validated")
        
        validate_anycast_password('bgp',enable_password)
        display_msg("PASS: Anycast enable password successfully validated")
        
        display_msg("---------Test Case 32 Execution Completed----------")

# Reboot

    @pytest.mark.run(order=33)
    def test_033_Perform_reboot_operation(self):
        """
        Perform reboot operation on the grid
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 33 Execution Started           |")
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
        
        display_msg("---------Test Case 33 Execution Completed----------")

    @pytest.mark.run(order=34)
    def test_034_validate_anycast_ospf_ipv4_password_encryption_after_reboot(self):
        """
        Validate that the anycast password from the CLI show command is encrypted after reboot operation
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 34 Execution Started          |")
        display_msg("----------------------------------------------------")
        display_msg("Getting the actual password from ospfd.conf file")
        password, enable_password = get_anycast_password('ospf')
        if not password or not enable_password:
            display_msg("FAIL: Failed to fetch the password")
            assert False
        
        display_msg("Getting the encrypted password from CLI output")
        pswd, en_pswd = get_pswd_from_cli('ospf')
        if not pswd or not en_pswd:
            display_msg("FAIL: Failed to fetch the password")
            assert False
        
        if password in pswd:
            display_msg("FAIL: CLI output of anycast password is not encrypted")
            assert False
        display_msg("PASS: CLI output of anycast password is encrypted")
        
        if enable_password in en_pswd:
            display_msg("FAIL: CLI output of anycast enable password is not encrypted")
            assert False
        display_msg("PASS: CLI output of anycast enable password is encrypted")
        
        validate_anycast_password('ospf',password)
        display_msg("PASS: Anycast password successfully validated")
        
        validate_anycast_password('ospf',enable_password)
        display_msg("PASS: Anycast enable password successfully validated")
        
        display_msg("---------Test Case 34 Execution Completed----------")


    @pytest.mark.run(order=35)
    def test_035_validate_anycast_ospf_ipv6_password_encryption_after_reboot(self):
        """
        Validate that the anycast password from the CLI show command is encrypted after reboot operation
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 35 Execution Started          |")
        display_msg("----------------------------------------------------")
        display_msg("Getting the actual password from ospf6d.conf file")
        password, enable_password = get_anycast_password('ospf6')
        if not password or not enable_password:
            display_msg("FAIL: Failed to fetch the password")
            assert False
        
        display_msg("Getting the encrypted password from CLI output")
        pswd, en_pswd = get_pswd_from_cli('ipv6_ospf')
        if not pswd or not en_pswd:
            display_msg("FAIL: Failed to fetch the password")
            assert False
        
        if password in pswd:
            display_msg("FAIL: CLI output of anycast password is not encrypted")
            assert False
        display_msg("PASS: CLI output of anycast password is encrypted")
        
        if enable_password in en_pswd:
            display_msg("FAIL: CLI output of anycast enable password is not encrypted")
            assert False
        display_msg("PASS: CLI output of anycast enable password is encrypted")
        
        validate_anycast_password('ospf6',password)
        display_msg("PASS: Anycast password successfully validated")
        
        validate_anycast_password('ospf6',enable_password)
        display_msg("PASS: Anycast enable password successfully validated")
        
        display_msg("---------Test Case 35 Execution Completed----------")

    @pytest.mark.run(order=36)
    def test_036_validate_anycast_bgp_ipv4_password_encryption_after_reboot(self):
        """
        Validate that the anycast password from the CLI show command is encrypted after reboot operation
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 36 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Getting the actual password from bgpd.conf file")
        password, enable_password = get_anycast_password('bgp')
        if not password or not enable_password:
            display_msg("FAIL: Failed to fetch the password")
            assert False
        
        display_msg("Getting the encrypted password from CLI output")
        pswd, en_pswd = get_pswd_from_cli('bgp')
        if not pswd or not en_pswd:
            display_msg("FAIL: Failed to fetch the password")
            assert False
        
        if password in pswd:
            display_msg("FAIL: CLI output of anycast password is not encrypted")
            assert False
        display_msg("PASS: CLI output of anycast password is encrypted")
        
        if enable_password in en_pswd:
            display_msg("FAIL: CLI output of anycast enable password is not encrypted")
            assert False
        display_msg("PASS: CLI output of anycast enable password is encrypted")
        
        validate_anycast_password('bgp',password)
        display_msg("PASS: Anycast password successfully validated")
        
        validate_anycast_password('bgp',enable_password)
        display_msg("PASS: Anycast enable password successfully validated")
        
        display_msg("---------Test Case 36 Execution Completed----------")


    @pytest.mark.run(order=37)
    def test_037_validate_anycast_bgp_ipv6_password_encryption_after_reboot(self):
        """
        Validate that the anycast password from the CLI show command is encrypted after reboot operation
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 37 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Getting the actual password from bgpd.conf file")
        password, enable_password = get_anycast_password('bgp')
        if not password or not enable_password:
            display_msg("FAIL: Failed to fetch the password")
            assert False
        
        display_msg("Getting the encrypted password from CLI output")
        pswd, en_pswd = get_pswd_from_cli('ipv6_bgp')
        if not pswd or not en_pswd:
            display_msg("FAIL: Failed to fetch the password")
            assert False
        
        if password in pswd:
            display_msg("FAIL: CLI output of anycast password is not encrypted")
            assert False
        display_msg("PASS: CLI output of anycast password is encrypted")
        
        if enable_password in en_pswd:
            display_msg("FAIL: CLI output of anycast enable password is not encrypted")
            assert False
        display_msg("PASS: CLI output of anycast enable password is encrypted")
        
        validate_anycast_password('bgp',password)
        display_msg("PASS: Anycast password successfully validated")
        
        validate_anycast_password('bgp',enable_password)
        display_msg("PASS: Anycast enable password successfully validated")
        
        display_msg("---------Test Case 37 Execution Completed----------")

# Support Bundle

    @pytest.mark.run(order=38)
    def test_038_download_support_bundle(self):
        """
        Download support Bundle
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 38 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Download support Bundle")
        data = {"member":config.grid_fqdn,
                "core_files":True,
                "log_files":True,
                "rotate_log_files":True}
        response = ib_NIOS.wapi_request('POST', object_type='fileop?_function=get_support_bundle', fields=json.dumps(data))
        if type(response) == tuple:
            display_msg(json.loads(response[1])['text'])
            display_msg("FAIL: Failed to download support bundle. Debug above log messages to find the root cause")
            assert False
        
        display_msg(response)
        url = json.loads(response)['url']
        output = os.popen('curl -k1 -u admin:infoblox -H "Content-type:application/force-download" -O '+url).read()
        display_msg(output)
        
        display_msg("---------Test Case 38 Execution Completed----------")

    @pytest.mark.run(order=39)
    def test_039_validate_support_bundle(self):
        """
        Validate support Bundle
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 39 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Validate support Bundle")
        output = os.popen('ls').read()
        if 'supportBundle'not in output:
            display_msg("SupportBundle is not downloaded in this location")
            assert False
        cwd = os.getcwd()
        cmd = "tar -xvzf supportBundle.tar.gz -C "+cwd+"/supportBundle/"
        extract_files = os.popen(cmd).read()
        display_msg(extract_files)
        
        # ospfd.conf
        ospfd = os.popen("cat "+cwd+"/supportBundle/ospfd.conf").read()
        for line in ospfd.split('\n'):
            match = re.match("^password (.+)$", line)
            if match:
                display_msg("Password: "+match.group(1))
                if "****" != match.group(1):
                    display_msg("FAIL: Password is not masked in ospfd.cof file from supportBundle")
                    assert False
                display_msg("PASS: Password is masked in ospfd.conf")
                break
        
        # ospf6d.conf
        ospf6d = os.popen("cat "+cwd+"/supportBundle/ospf6d.conf").read()
        for line in ospf6d.split('\n'):
            match = re.match("^password (.+)$", line)
            if match:
                display_msg("Password: "+match.group(1))
                if "****" != match.group(1):
                    display_msg("FAIL: Password is not masked in ospf6d.cof file from supportBundle")
                    assert False
                display_msg("PASS: Password is masked in ospf6d.conf")
                break
        
        # bgpd.conf
        bgpd = os.popen("cat "+cwd+"/supportBundle/bgpd.conf").read()
        for line in bgpd.split('\n'):
            match = re.match("^password (.+)$", line)
            if match:
                display_msg("Password: "+match.group(1))
                if "****" != match.group(1):
                    display_msg("FAIL: Password is not masked in bgpd.cof file from supportBundle")
                    assert False
                display_msg("PASS: Password is masked in bgpd.conf")
                break
        
        # bfdd.conf
        bfdd = os.popen("cat "+cwd+"/supportBundle/bfdd.conf").read()
        for line in bfdd.split('\n'):
            match = re.match("^password (.+)$", line)
            if match:
                display_msg("Password: "+match.group(1))
                if "****" != match.group(1):
                    display_msg("FAIL: Password is not masked in bfdd.cof file from supportBundle")
                    assert False
                display_msg("PASS: Password is masked in bfdd.conf")
                break
        
        display_msg("---------Test Case 39 Execution Completed----------")

# GMC Promotion

    @pytest.mark.run(order=40)
    def test_040_set_member_as_master_candidate(self):
        """
        Set member as master candidate
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 40 Execution Started           |")
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
        
        display_msg("---------Test Case 40 Execution Completed----------")

    @pytest.mark.run(order=41)
    def test_041_Perform_gmc_promotion(self):
        """
        Perform GMC Promotion on the Master Candidate
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 41 Execution Started           |")
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
        
        display_msg("---------Test Case 41 Execution Completed----------")

# Validation

    @pytest.mark.run(order=42)
    def test_042_validate_ospf_ipv4_anycast_service_promoted_master(self):
        """
        Dig using anycast IP address and validate anycast service
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 42 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Perform dig operation using Anycast interface")
        validate_anycast_service('11.1.1.2')
        
        display_msg("---------Test Case 42 Execution Completed----------")

    @pytest.mark.run(order=43)
    def test_043_validate_anycast_ospf_ipv4_password_encryption_promoted_master(self):
        """
        Validate that the anycast password from the CLI show command is encrypted
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 43 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Getting the actual password from ospfd.conf file")
        password, enable_password = get_anycast_password('ospf')
        if not password or not enable_password:
            display_msg("FAIL: Failed to fetch the password")
            assert False
        
        display_msg("Getting the encrypted password from CLI output")
        pswd, en_pswd = get_pswd_from_cli('ospf')
        if not pswd or not en_pswd:
            display_msg("FAIL: Failed to fetch the password")
            assert False
        
        if password in pswd:
            display_msg("FAIL: CLI output of anycast password is not encrypted")
            assert False
        display_msg("PASS: CLI output of anycast password is encrypted")
        
        if enable_password in en_pswd:
            display_msg("FAIL: CLI output of anycast enable password is not encrypted")
            assert False
        display_msg("PASS: CLI output of anycast enable password is encrypted")
        
        validate_anycast_password('ospf',password)
        display_msg("PASS: Anycast password successfully validated")
        
        validate_anycast_password('ospf',enable_password)
        display_msg("PASS: Anycast enable password successfully validated")
        
        display_msg("---------Test Case 43 Execution Completed----------")

    @pytest.mark.run(order=44)
    def test_044_validate_ospf_ipv6_anycast_service_promoted_master(self):
        """
        Dig using anycast IP address and validate anycast service
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 44 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Perform dig operation using IPV6 Anycast interface")
        validate_anycast_service('1111::2222')
        
        display_msg("---------Test Case 44 Execution Completed----------")

    @pytest.mark.run(order=45)
    def test_045_validate_anycast_ospf_ipv6_password_encryption_promoted_master(self):
        """
        Validate that the anycast password from the CLI show command is encrypted
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 45 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Getting the actual password from ospf6d.conf file")
        password, enable_password = get_anycast_password('ospf6')
        if not password or not enable_password:
            display_msg("FAIL: Failed to fetch the password")
            assert False
        
        display_msg("Getting the encrypted password from CLI output")
        pswd, en_pswd = get_pswd_from_cli('ipv6_ospf')
        if not pswd or not en_pswd:
            display_msg("FAIL: Failed to fetch the password")
            assert False
        
        if password in pswd:
            display_msg("FAIL: CLI output of anycast password is not encrypted")
            assert False
        display_msg("PASS: CLI output of anycast password is encrypted")
        
        if enable_password in en_pswd:
            display_msg("FAIL: CLI output of anycast enable password is not encrypted")
            assert False
        display_msg("PASS: CLI output of anycast enable password is encrypted")
        
        validate_anycast_password('ospf6',password)
        display_msg("PASS: Anycast password successfully validated")
        
        validate_anycast_password('ospf6',enable_password)
        display_msg("PASS: Anycast enable password successfully validated")
        
        display_msg("---------Test Case 45 Execution Completed----------")
        
    @pytest.mark.run(order=46)
    def test_046_validate_bgp_ipv4_anycast_service_promoted_master(self):
        """
        Dig using anycast IP address and validate anycast service
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 46 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Perform dig operation using Anycast interface")
        validate_anycast_service('11.1.1.3')
        
        display_msg("---------Test Case 46 Execution Completed----------")

    @pytest.mark.run(order=47)
    def test_047_validate_anycast_bgp_ipv4_password_encryption_promoted_master(self):
        """
        Validate that the anycast password from the CLI show command is encrypted
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 47 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Getting the actual password from bgpd.conf file")
        password, enable_password = get_anycast_password('bgp')
        if not password or not enable_password:
            display_msg("FAIL: Failed to fetch the password")
            assert False
        
        display_msg("Getting the encrypted password from CLI output")
        pswd, en_pswd = get_pswd_from_cli('bgp')
        if not pswd or not en_pswd:
            display_msg("FAIL: Failed to fetch the password")
            assert False
        
        if password in pswd:
            display_msg("FAIL: CLI output of anycast password is not encrypted")
            assert False
        display_msg("PASS: CLI output of anycast password is encrypted")
        
        if enable_password in en_pswd:
            display_msg("FAIL: CLI output of anycast enable password is not encrypted")
            assert False
        display_msg("PASS: CLI output of anycast enable password is encrypted")
        
        validate_anycast_password('bgp',password)
        display_msg("PASS: Anycast password successfully validated")
        
        validate_anycast_password('bgp',enable_password)
        display_msg("PASS: Anycast enable password successfully validated")
        
        display_msg("---------Test Case 47 Execution Completed----------")

    @pytest.mark.run(order=48)
    def test_048_validate_bgp_ipv6_anycast_service_promoted_master(self):
        """
        Dig using anycast IP address and validate anycast service
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 48 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Perform dig operation using Anycast interface")
        validate_anycast_service('2222::1111')
        
        display_msg("---------Test Case 48 Execution Completed----------")

    @pytest.mark.run(order=49)
    def test_049_validate_anycast_bgp_ipv6_password_encryption_promoted_master(self):
        """
        Validate that the anycast password from the CLI show command is encrypted
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 49 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Getting the actual password from bgpd.conf file")
        password, enable_password = get_anycast_password('bgp')
        if not password or not enable_password:
            display_msg("FAIL: Failed to fetch the password")
            assert False
        
        display_msg("Getting the encrypted password from CLI output")
        pswd, en_pswd = get_pswd_from_cli('ipv6_bgp')
        if not pswd or not en_pswd:
            display_msg("FAIL: Failed to fetch the password")
            assert False
        
        if password in pswd:
            display_msg("FAIL: CLI output of anycast password is not encrypted")
            assert False
        display_msg("PASS: CLI output of anycast password is encrypted")
        
        if enable_password in en_pswd:
            display_msg("FAIL: CLI output of anycast enable password is not encrypted")
            assert False
        display_msg("PASS: CLI output of anycast enable password is encrypted")
        
        validate_anycast_password('bgp',password)
        display_msg("PASS: Anycast password successfully validated")
        
        validate_anycast_password('bgp',enable_password)
        display_msg("PASS: Anycast enable password successfully validated")
        
        display_msg("---------Test Case 49 Execution Completed----------")

    @pytest.mark.run(order=50)
    def test_050_Perform_gmc_promotion_on_old_master(self):
        """
        Perform GMC Promotion on the old Master to make it Master again
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 50 Execution Started           |")
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
        
        display_msg("---------Test Case 50 Execution Completed----------")

# HA Failover

    @pytest.mark.run(order=51)
    def test_051_Perform_ha_failover(self):
        """
        Perform HA Failover
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 51 Execution Started          |")
        display_msg("----------------------------------------------------")
        display_msg("Perform HA Failover")
        get_ref = ib_NIOS.wapi_request('GET', object_type='member')
        display_msg(get_ref)
        data = {"operation":"FORCE_FAILOVER"}
        response = ib_NIOS.wapi_request('POST', object_type=json.loads(get_ref)[0]['_ref']+'?_function=member_admin_operation', fields=json.dumps(data))
        if type(response) == tuple:
            display_msg(json.loads(response[1])['text'])
            display_msg("FAIL: Failed to perform HA failover. Debug above log messages to find the root cause")
            assert False
        
        display_msg("PASS: HA Failover done")
        display_msg("Sleep for 10 minutes")
        sleep(700)
        count = 0
        while not is_grid_alive():
            if count == 5:
                display_msg("Giving up after 5 tries")
                assert False
            display_msg("Sleeping for 1 more minute...")
            sleep(60)
            count += 1
        
        display_msg("---------Test Case 51 Execution Completed----------")

    @pytest.mark.run(order=52)
    def test_052_validate_ospf_ipv4_anycast_service_after_ha_failover(self):
        """
        Dig using anycast IP address and validate anycast service
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 52 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Perform dig operation using Anycast interface")
        validate_anycast_service('11.1.1.2')
        
        display_msg("---------Test Case 52 Execution Completed----------")

    @pytest.mark.run(order=53)
    def test_053_validate_anycast_ospf_ipv4_password_encryption_after_ha_failover(self):
        """
        Validate that the anycast password from the CLI show command is encrypted
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 53 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Getting the actual password from ospfd.conf file")
        password, enable_password = get_anycast_password('ospf')
        if not password or not enable_password:
            display_msg("FAIL: Failed to fetch the password")
            assert False
        
        display_msg("Getting the encrypted password from CLI output")
        pswd, en_pswd = get_pswd_from_cli('ospf')
        if not pswd or not en_pswd:
            display_msg("FAIL: Failed to fetch the password")
            assert False
        
        if password in pswd:
            display_msg("FAIL: CLI output of anycast password is not encrypted")
            assert False
        display_msg("PASS: CLI output of anycast password is encrypted")
        
        if enable_password in en_pswd:
            display_msg("FAIL: CLI output of anycast enable password is not encrypted")
            assert False
        display_msg("PASS: CLI output of anycast enable password is encrypted")
        
        validate_anycast_password('ospf',password)
        display_msg("PASS: Anycast password successfully validated")
        
        validate_anycast_password('ospf',enable_password)
        display_msg("PASS: Anycast enable password successfully validated")
        
        display_msg("---------Test Case 53 Execution Completed----------")

    @pytest.mark.run(order=54)
    def test_054_validate_ospf_ipv6_anycast_service_after_ha_failover(self):
        """
        Dig using anycast IP address and validate anycast service
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 54 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Perform dig operation using IPV6 Anycast interface")
        validate_anycast_service('1111::2222')
        
        display_msg("---------Test Case 54 Execution Completed----------")

    @pytest.mark.run(order=55)
    def test_055_validate_anycast_ospf_ipv6_password_encryption_after_ha_failover(self):
        """
        Validate that the anycast password from the CLI show command is encrypted
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 55 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Getting the actual password from ospf6d.conf file")
        password, enable_password = get_anycast_password('ospf6')
        if not password or not enable_password:
            display_msg("FAIL: Failed to fetch the password")
            assert False
        
        display_msg("Getting the encrypted password from CLI output")
        pswd, en_pswd = get_pswd_from_cli('ipv6_ospf')
        if not pswd or not en_pswd:
            display_msg("FAIL: Failed to fetch the password")
            assert False
        
        if password in pswd:
            display_msg("FAIL: CLI output of anycast password is not encrypted")
            assert False
        display_msg("PASS: CLI output of anycast password is encrypted")
        
        if enable_password in en_pswd:
            display_msg("FAIL: CLI output of anycast enable password is not encrypted")
            assert False
        display_msg("PASS: CLI output of anycast enable password is encrypted")
        
        validate_anycast_password('ospf6',password)
        display_msg("PASS: Anycast password successfully validated")
        
        validate_anycast_password('ospf6',enable_password)
        display_msg("PASS: Anycast enable password successfully validated")
        
        display_msg("---------Test Case 55 Execution Completed----------")
        
    @pytest.mark.run(order=56)
    def test_056_validate_bgp_ipv4_anycast_service_after_ha_failover(self):
        """
        Dig using anycast IP address and validate anycast service
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 56 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Perform dig operation using Anycast interface")
        validate_anycast_service('11.1.1.3')
        
        display_msg("---------Test Case 56 Execution Completed----------")

    @pytest.mark.run(order=57)
    def test_057_validate_anycast_bgp_ipv4_password_encryption_after_ha_failover(self):
        """
        Validate that the anycast password from the CLI show command is encrypted
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 57 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Getting the actual password from bgpd.conf file")
        password, enable_password = get_anycast_password('bgp')
        if not password or not enable_password:
            display_msg("FAIL: Failed to fetch the password")
            assert False
        
        display_msg("Getting the encrypted password from CLI output")
        pswd, en_pswd = get_pswd_from_cli('bgp')
        if not pswd or not en_pswd:
            display_msg("FAIL: Failed to fetch the password")
            assert False
        
        if password in pswd:
            display_msg("FAIL: CLI output of anycast password is not encrypted")
            assert False
        display_msg("PASS: CLI output of anycast password is encrypted")
        
        if enable_password in en_pswd:
            display_msg("FAIL: CLI output of anycast enable password is not encrypted")
            assert False
        display_msg("PASS: CLI output of anycast enable password is encrypted")
        
        validate_anycast_password('bgp',password)
        display_msg("PASS: Anycast password successfully validated")
        
        validate_anycast_password('bgp',enable_password)
        display_msg("PASS: Anycast enable password successfully validated")
        
        display_msg("---------Test Case 57 Execution Completed----------")

    @pytest.mark.run(order=58)
    def test_058_validate_bgp_ipv6_anycast_service_after_ha_failover(self):
        """
        Dig using anycast IP address and validate anycast service
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 58 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Perform dig operation using Anycast interface")
        validate_anycast_service('2222::1111')
        
        display_msg("---------Test Case 58 Execution Completed----------")

    @pytest.mark.run(order=59)
    def test_059_validate_anycast_bgp_ipv6_password_encryption_after_ha_failover(self):
        """
        Validate that the anycast password from the CLI show command is encrypted
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 59 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Getting the actual password from bgpd.conf file")
        password, enable_password = get_anycast_password('bgp')
        if not password or not enable_password:
            display_msg("FAIL: Failed to fetch the password")
            assert False
        
        display_msg("Getting the encrypted password from CLI output")
        pswd, en_pswd = get_pswd_from_cli('ipv6_bgp')
        if not pswd or not en_pswd:
            display_msg("FAIL: Failed to fetch the password")
            assert False
        
        if password in pswd:
            display_msg("FAIL: CLI output of anycast password is not encrypted")
            assert False
        display_msg("PASS: CLI output of anycast password is encrypted")
        
        if enable_password in en_pswd:
            display_msg("FAIL: CLI output of anycast enable password is not encrypted")
            assert False
        display_msg("PASS: CLI output of anycast enable password is encrypted")
        
        validate_anycast_password('bgp',password)
        display_msg("PASS: Anycast password successfully validated")
        
        validate_anycast_password('bgp',enable_password)
        display_msg("PASS: Anycast enable password successfully validated")
        
        display_msg("---------Test Case 59 Execution Completed----------")

#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

# CLI testing

    @pytest.mark.run(order=60)
    def test_060_Execute_set_regenerate_anycast_password_CLI(self):
        """
        Execute set regenerate_anycast_password CLI
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 60 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Execute set regenerate_anycast_password CLI")
        
        global password1
        global enable_password1
        
        # start log capture
        display_msg("Start log capture")
        log("start","/infoblox/var/infoblox.log",config.grid_vip)
        
        display_msg("Getting the actual password from ospfd.conf file beofre executing the CLI")
        password1, enable_password1 = get_anycast_password('ospf')
        if not password1 and enable_password1:
            display_msg("FAIL: Failed to fetch the password")
            assert False
        
        args = "sshpass -p 'infoblox' ssh -o StrictHostKeyChecking=no admin@"+config.grid_vip
        args = shlex.split(args)
        child = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        child.stdin.write("set maintenancemode\n")
        child.stdin.write("set regenerate_anycast_password\n")
        child.stdin.write("y\n")
        child.stdin.write("y\n")
        output = child.communicate()
        flag = False
        for line in output:
            display_msg(line)
            if 'Anycast password generation is successful' in line:
                flag = True
        if flag:
            display_msg("PASS: Execution of the CLI passed")
        else:
            display_msg("FAIL: Execution of the CLI failed")
            assert False
        
        display_msg("Sleep for 3 minutes")
        sleep(200)
        
        # stop log capture
        display_msg("Stop log capture")
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
        
        # validate captured log
        display_msg("Validate log for anycast service restart")
        logv("\'Starting bfdd process\'","/infoblox/var/infoblox.log",config.grid_vip)
        logv("\'Starting bgpd process\'","/infoblox/var/infoblox.log",config.grid_vip)
        logv("\'Starting ospfd process\'","/infoblox/var/infoblox.log",config.grid_vip)
        logv("\'Starting ospf6d process\'","/infoblox/var/infoblox.log",config.grid_vip)
        
        display_msg("---------Test Case 60 Execution Completed----------")

# Validation
    @pytest.mark.run(order=61)
    def test_061_validate_new_anycast_ospf_ipv4_password_encryption(self):
        """
        Validate that the newly generated anycast password from the CLI show command is encrypted
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 61 Execution Started          |")
        display_msg("----------------------------------------------------")
        
        global password1
        global enable_password1
        display_msg("Getting the actual password from ospfd.conf file")
        password2, enable_password2 = get_anycast_password('ospf')
        if not password2:
            display_msg("FAIL: Failed to fetch the password")
            assert False
        
        display_msg("Getting the encrypted password from CLI output")
        pswd, en_pswd = get_pswd_from_cli('ospf')
        if not en_pswd:
            display_msg("FAIL: Failed to fetch the password")
            assert False
        
        if password2 in pswd:
            display_msg("FAIL: CLI output of anycast password is not encrypted")
            assert False
        display_msg("PASS: CLI output of anycast password is encrypted")
        
        if enable_password2 in en_pswd:
            display_msg("FAIL: CLI output of anycast enable password is not encrypted")
            assert False
        display_msg("PASS: CLI output of anycast enable password is encrypted")
        
        if password1 in password2:
            display_msg("FAIL: New anycast password is not generated")
            assert False
        display_msg("PASS: New anycast password is generated")
        
        if enable_password1 in enable_password2:
            display_msg("FAIL: New anycast enable password is not generated")
            assert False
        display_msg("PASS: New anycast enable password is generated")
        
        validate_anycast_password('ospf',password2)
        display_msg("PASS: Anycast password successfully validated")
        
        validate_anycast_password('ospf',enable_password2)
        display_msg("PASS: Anycast enable password successfully validated")
        
        display_msg("---------Test Case 61 Execution Completed----------")

    @pytest.mark.run(order=62)
    def test_062_add_radius_user(self):
        """
        Add Radius user
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 62 Execution Started          |")
        display_msg("----------------------------------------------------")
        
        display_msg("Adding Radius user")
        data = {"name":"rad_user",
                "servers": [{"address":config.radius_server,
                            "shared_secret":config.radius_secrete
                           }]
                }
        response = ib_NIOS.wapi_request('POST', object_type='radius:authservice',fields=json.dumps(data))
        if type(response) == tuple:
            display_msg(json.loads(response[1])['text'])
            display_msg("FAIL: Failed to add radius user. Debug above log messages to find the root cause")
            assert False
        display_msg(response)
        display_msg("PASS: Successfully added radius user")
        
        # Adding radius server in authpolicy
        display_msg("Add radius server in authentication policy")
        get_ref = ib_NIOS.wapi_request('GET', object_type='authpolicy?_return_fields=auth_services')
        display_msg(get_ref)
        ref = json.loads(get_ref)[0]
        old_data = ref["auth_services"]
        data2 = {"auth_services":[json.loads(response)]}
        data2["auth_services"].extend(old_data)
        response2 = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data2))
        if type(response2) == tuple:
            display_msg(json.loads(response2[1])['text'])
            display_msg("FAIL: Failed to add radius server in authpolicy. Debug above log messages to find the root cause")
            assert False
        display_msg(response2)
        display_msg("PASS: Successfully added radius server in authpolicy")
        
        map_remote_user_to_the_group()
        
        display_msg("---------Test Case 62 Execution Completed----------")
        
    @pytest.mark.run(order=63)
    def test_063_validate_radius_user(self):
        """
        Validate Radius user
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 63 Execution Started          |")
        display_msg("----------------------------------------------------")
        
        display_msg("Validate Radius user")
        response = ib_NIOS.wapi_request('GET', object_type='radius:authservice')
        display_msg(response)
        if 'rad_user' not in response:
            display_msg("FAIL: Failed to validate radius user")
            assert False
        display_msg("PASS: Successfully validated radius user")
        
        # Validate authpolicy
        display_msg("Validate Radius server in authpolicy")
        get_ref = ib_NIOS.wapi_request('GET', object_type='authpolicy?_return_fields=auth_services')
        display_msg(get_ref)
        if 'rad_user' not in response:
            display_msg("FAIL: Failed to validate radius server in authpolicy")
            assert False
        display_msg("PASS: Successfully validated radius server in authpolicy")
        
        display_msg("---------Test Case 63 Execution Completed----------")

    @pytest.mark.run(order=64)
    def test_064_add_tacacs_user(self):
        """
        Add Tacacs+ user
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 64 Execution Started          |")
        display_msg("----------------------------------------------------")
        
        display_msg("Adding Tacacs+ user")
        data = {"name":"tac_plus_user",
                "servers": [{"address":config.tac_plus_server,
                            "shared_secret":config.tac_plus_secrete
                           }]
                }
        response = ib_NIOS.wapi_request('POST', object_type='tacacsplus:authservice',fields=json.dumps(data))
        if type(response) == tuple:
            display_msg(json.loads(response[1])['text'])
            display_msg("FAIL: Failed to add tacacs+ user. Debug above log messages to find the root cause")
            assert False
        display_msg(response)
        display_msg("PASS: Successfully added tacacs+ user")
        
        # Adding tacacs+ server in authpolicy
        display_msg("Add tacacs+ server in authentication policy")
        get_ref = ib_NIOS.wapi_request('GET', object_type='authpolicy?_return_fields=auth_services')
        display_msg(get_ref)
        ref = json.loads(get_ref)[0]
        old_data = ref["auth_services"]
        data2 = {"auth_services":[json.loads(response)]}
        data2["auth_services"].extend(old_data)
        response2 = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data2))
        if type(response2) == tuple:
            display_msg(json.loads(response2[1])['text'])
            display_msg("FAIL: Failed to add tacacs+ server in authpolicy. Debug above log messages to find the root cause")
            assert False
        display_msg(response2)
        display_msg("PASS: Successfully added tacacs+ server in authpolicy")
        
        map_remote_user_to_the_group()
        
        display_msg("---------Test Case 64 Execution Completed----------")
        
    @pytest.mark.run(order=65)
    def test_065_validate_tac_plus_user(self):
        """
        Validate Tacacs+ user
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 65 Execution Started          |")
        display_msg("----------------------------------------------------")
        
        display_msg("Validate Tacacs+ user")
        response = ib_NIOS.wapi_request('GET', object_type='tacacsplus:authservice')
        display_msg(response)
        if 'tac_plus_user' not in response:
            display_msg("FAIL: Failed to validate tacacs+ user")
            assert False
        display_msg("PASS: Successfully validated tacacs+ user")
        
        # Validate authpolicy
        display_msg("Validate Tacacs+ server in authpolicy")
        get_ref = ib_NIOS.wapi_request('GET', object_type='authpolicy?_return_fields=auth_services')
        display_msg(get_ref)
        if 'tac_plus_user' not in response:
            display_msg("FAIL: Failed to validate Tacacs+ server in authpolicy")
            assert False
        display_msg("PASS: Successfully validated Tacacs+ server in authpolicy")
        
        display_msg("---------Test Case 65 Execution Completed----------")

# Validate password encryption using radius user

    @pytest.mark.run(order=66)
    def test_066_validate_anycast_ospf_ipv4_password_encryption_using_radius_user(self):
        """
        Validate ospf ipv4 password encryption using radius user
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 66 Execution Started          |")
        display_msg("----------------------------------------------------")
        display_msg("Getting the actual password from ospfd.conf file")
        password, enable_password = get_anycast_password('ospf')
        if not password or not enable_password:
            display_msg("FAIL: Failed to fetch the password")
            assert False
        
        display_msg("Getting the encrypted password from CLI output")
        pswd, en_pswd = get_pswd_from_cli('ospf',user=config.radius_user,password=config.radius_password)
        if not pswd or not en_pswd:
            display_msg("FAIL: Failed to fetch the password")
            assert False
        
        if password in pswd:
            display_msg("FAIL: CLI output of anycast password is not encrypted")
            assert False
        display_msg("PASS: CLI output of anycast password is encrypted")
        
        if enable_password in en_pswd:
            display_msg("FAIL: CLI output of anycast enable password is not encrypted")
            assert False
        display_msg("PASS: CLI output of anycast enable password is encrypted")
        
        display_msg("---------Test Case 66 Execution Completed----------")

    @pytest.mark.run(order=67)
    def test_067_validate_anycast_ospf_ipv6_password_encryption_using_radius_user(self):
        """
        Validate ospf ipv6 password encryption using radius user
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 67 Execution Started          |")
        display_msg("----------------------------------------------------")
        display_msg("Getting the actual password from ospf6d.conf file")
        password, enable_password = get_anycast_password('ospf6')
        if not password or not enable_password:
            display_msg("FAIL: Failed to fetch the password")
            assert False
        
        display_msg("Getting the encrypted password from CLI output")
        pswd, en_pswd = get_pswd_from_cli('ipv6_ospf',user=config.radius_user,password=config.radius_password)
        if not pswd or not en_pswd:
            display_msg("FAIL: Failed to fetch the password")
            assert False
        
        if password in pswd:
            display_msg("FAIL: CLI output of anycast password is not encrypted")
            assert False
        display_msg("PASS: CLI output of anycast password is encrypted")
        
        if enable_password in en_pswd:
            display_msg("FAIL: CLI output of anycast enable password is not encrypted")
            assert False
        display_msg("PASS: CLI output of anycast enable password is encrypted")
        
        display_msg("---------Test Case 67 Execution Completed----------")

    @pytest.mark.run(order=68)
    def test_068_validate_anycast_bgp_ipv4_password_encryption_using_radius_user(self):
        """
        Validate bgp ipv4 password encryption using radius user
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 68 Execution Started          |")
        display_msg("----------------------------------------------------")
        display_msg("Getting the actual password from bgpd.conf file")
        password, enable_password = get_anycast_password('bgp')
        if not password or not enable_password:
            display_msg("FAIL: Failed to fetch the password")
            assert False
        
        display_msg("Getting the encrypted password from CLI output")
        pswd, en_pswd = get_pswd_from_cli('bgp',user=config.radius_user,password=config.radius_password)
        if not pswd or not en_pswd:
            display_msg("FAIL: Failed to fetch the password")
            assert False
        
        if password in pswd:
            display_msg("FAIL: CLI output of anycast password is not encrypted")
            assert False
        display_msg("PASS: CLI output of anycast password is encrypted")
        
        if enable_password in en_pswd:
            display_msg("FAIL: CLI output of anycast enable password is not encrypted")
            assert False
        display_msg("PASS: CLI output of anycast enable password is encrypted")
        
        display_msg("---------Test Case 68 Execution Completed----------")

    @pytest.mark.run(order=69)
    def test_069_validate_anycast_bgp_ipv4_password_encryption_using_radius_user(self):
        """
        Validate bgp ipv6 password encryption using radius user
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 69 Execution Started          |")
        display_msg("----------------------------------------------------")
        display_msg("Getting the actual password from bgpd.conf file")
        password, enable_password = get_anycast_password('bgp')
        if not password or not enable_password:
            display_msg("FAIL: Failed to fetch the password")
            assert False
        
        display_msg("Getting the encrypted password from CLI output")
        pswd, en_pswd = get_pswd_from_cli('ipv6_bgp',user=config.radius_user,password=config.radius_password)
        if not pswd or not en_pswd:
            display_msg("FAIL: Failed to fetch the password")
            assert False
        
        if password in pswd:
            display_msg("FAIL: CLI output of anycast password is not encrypted")
            assert False
        display_msg("PASS: CLI output of anycast password is encrypted")
        
        if enable_password in en_pswd:
            display_msg("FAIL: CLI output of anycast enable password is not encrypted")
            assert False
        display_msg("PASS: CLI output of anycast enable password is encrypted")
        
        display_msg("---------Test Case 69 Execution Completed----------")

# Validate password encryption using tacacs user

    @pytest.mark.run(order=70)
    def test_070_validate_anycast_ospf_ipv4_password_encryption_using_tac_plus_user(self):
        """
        Validate ospf ipv4 password encryption using tacacs+ user
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 70 Execution Started          |")
        display_msg("----------------------------------------------------")
        display_msg("Getting the actual password from ospfd.conf file")
        password, enable_password = get_anycast_password('ospf')
        if not password or not enable_password:
            display_msg("FAIL: Failed to fetch the password")
            assert False
        
        display_msg("Getting the encrypted password from CLI output")
        pswd, en_pswd = get_pswd_from_cli('ospf',user=config.tac_plus_user,password=config.tac_plus_password)
        if not pswd or not en_pswd:
            display_msg("FAIL: Failed to fetch the password")
            assert False
        
        if password in pswd:
            display_msg("FAIL: CLI output of anycast password is not encrypted")
            assert False
        display_msg("PASS: CLI output of anycast password is encrypted")
        
        if enable_password in en_pswd:
            display_msg("FAIL: CLI output of anycast enable password is not encrypted")
            assert False
        display_msg("PASS: CLI output of anycast enable password is encrypted")
        
        display_msg("---------Test Case 70 Execution Completed----------")

    @pytest.mark.run(order=71)
    def test_071_validate_anycast_ospf_ipv6_password_encryption_using_tac_plus_user(self):
        """
        Validate ospf ipv6 password encryption using tacacs+ user
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 71 Execution Started          |")
        display_msg("----------------------------------------------------")
        display_msg("Getting the actual password from ospf6d.conf file")
        password, enable_password = get_anycast_password('ospf6')
        if not password or not enable_password:
            display_msg("FAIL: Failed to fetch the password")
            assert False
        
        display_msg("Getting the encrypted password from CLI output")
        pswd, en_pswd = get_pswd_from_cli('ipv6_ospf',user=config.tac_plus_user,password=config.tac_plus_password)
        if not pswd or not en_pswd:
            display_msg("FAIL: Failed to fetch the password")
            assert False
        
        if password in pswd:
            display_msg("FAIL: CLI output of anycast password is not encrypted")
            assert False
        display_msg("PASS: CLI output of anycast password is encrypted")
        
        if enable_password in en_pswd:
            display_msg("FAIL: CLI output of anycast enable password is not encrypted")
            assert False
        display_msg("PASS: CLI output of anycast enable password is encrypted")
        
        display_msg("---------Test Case 71 Execution Completed----------")

    @pytest.mark.run(order=72)
    def test_072_validate_anycast_bgp_ipv4_password_encryption_using_tac_plus_user(self):
        """
        Validate bgp ipv4 password encryption using tacacs+ user
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 72 Execution Started          |")
        display_msg("----------------------------------------------------")
        display_msg("Getting the actual password from bgpd.conf file")
        password, enable_password = get_anycast_password('bgp')
        if not password or not enable_password:
            display_msg("FAIL: Failed to fetch the password")
            assert False
        
        display_msg("Getting the encrypted password from CLI output")
        pswd, en_pswd = get_pswd_from_cli('bgp',user=config.tac_plus_user,password=config.tac_plus_password)
        if not pswd or not en_pswd:
            display_msg("FAIL: Failed to fetch the password")
            assert False
        
        if password in pswd:
            display_msg("FAIL: CLI output of anycast password is not encrypted")
            assert False
        display_msg("PASS: CLI output of anycast password is encrypted")
        
        if enable_password in en_pswd:
            display_msg("FAIL: CLI output of anycast enable password is not encrypted")
            assert False
        display_msg("PASS: CLI output of anycast enable password is encrypted")
        
        display_msg("---------Test Case 72 Execution Completed----------")

    @pytest.mark.run(order=73)
    def test_073_validate_anycast_bgp_ipv4_password_encryption_using_tac_plus_user(self):
        """
        Validate bgp ipv6 password encryption using tacacs+ user
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 73 Execution Started          |")
        display_msg("----------------------------------------------------")
        display_msg("Getting the actual password from bgpd.conf file")
        password, enable_password = get_anycast_password('bgp')
        if not password or not enable_password:
            display_msg("FAIL: Failed to fetch the password")
            assert False
        
        display_msg("Getting the encrypted password from CLI output")
        pswd, en_pswd = get_pswd_from_cli('ipv6_bgp',user=config.tac_plus_user,password=config.tac_plus_password)
        if not pswd or not en_pswd:
            display_msg("FAIL: Failed to fetch the password")
            assert False
        
        if password in pswd:
            display_msg("FAIL: CLI output of anycast password is not encrypted")
            assert False
        display_msg("PASS: CLI output of anycast password is encrypted")
        
        if enable_password in en_pswd:
            display_msg("FAIL: CLI output of anycast enable password is not encrypted")
            assert False
        display_msg("PASS: CLI output of anycast enable password is encrypted")
        
        display_msg("---------Test Case 73 Execution Completed----------")


# Restore Backup

    @pytest.mark.run(order=74)
    def test_074_Restore_backup_file_from_older_build_on_grid2(self):
        """
        Restore the backup file taken from a grid with older build where password is not encrypted (<= 8.6.0,8.5.3)
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 74 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Restore backup file")
        
        # Preparation
        
        output = os.popen("python anycast_network.py "+config.anycast_client_vm_id)
        display_msg(output)
        '''
        client_ip=os.popen("hostname -i").read()
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.grid2_vip, username='root', pkey = mykey)
        stdin, stdout, stderr = client.exec_command("scp root@"+client_ip+"://import/qaddi/raghavendra/clear_admin_password.py .")
        stdin, stdout, stderr = client.exec_command("touch /infoblox/var/debug_ssh_enabled")
        stdin, stdout, stderr = client.exec_command("touch /infoblox/var/old_supacc")
        for line in stdout.readlines():
            display_msg(line)
        client.close()
        '''
        
        # upload restore file
        dir_name=os.getcwd()
        base_filename = "rfe_11117.bak"
        token = generate_token_from_file(dir_name, base_filename, grid=config.grid2_vip)
        data = {"discovery_data":True,
                "keep_grid_ip":True,
                "mode":"FORCED",
                "token":token}
        response = ib_NIOS.wapi_request('POST', object_type='fileop?_function=restoredatabase', fields=json.dumps(data),grid_vip=config.grid2_vip)
        display_msg(response)
        if type(response) == tuple:
            display_msg(json.loads(response[1])['text'])
            display_msg("FAIL: Failed to upload database backup file. Debug above log messages to find the root cause")
            assert False
        
        display_msg("Sleep for 5 minutes")
        sleep(300)
        count = 0
        while not is_grid_alive():
            if count == 5:
                display_msg("Giving up after 5 tries")
                assert False
            display_msg("Sleeping for 1 more minute...")
            sleep(60)
            count += 1
        
        # clear admin password
        '''
        client_ip=os.popen("hostname -i").read()
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.grid2_vip, username='root', pkey = mykey)
        stdin, stdout, stderr = client.exec_command("python clear_admin_password.py")
        for line in stdout.readlines():
            display_msg(line)
        client.close()
        '''
        
        display_msg("---------Test Case 74 Execution Completed----------")

# Validation

    @pytest.mark.run(order=75)
    def test_075_validate_anycast_ospf_ipv4_password_encryption_grid2(self):
        """
        Validate that the anycast password from the CLI show command is encrypted in grid2 after backup restore
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 75 Execution Started          |")
        display_msg("----------------------------------------------------")
        display_msg("Getting the actual password from ospfd.conf file")
        password, enable_password = get_anycast_password('ospf')
        if not password or not enable_password:
            display_msg("FAIL: Failed to fetch the password")
            assert False
        
        display_msg("Getting the encrypted password from CLI output")
        pswd, en_pswd = get_pswd_from_cli('ospf')
        if not pswd or not en_pswd:
            display_msg("FAIL: Failed to fetch the password")
            assert False
        
        if password in pswd:
            display_msg("FAIL: CLI output of anycast password is not encrypted")
            assert False
        display_msg("PASS: CLI output of anycast password is encrypted")
        
        if enable_password in en_pswd:
            display_msg("FAIL: CLI output of anycast enable password is not encrypted")
            assert False
        display_msg("PASS: CLI output of anycast enable password is encrypted")
        
        validate_anycast_password('ospf',password)
        display_msg("PASS: Anycast password successfully validated")
        
        validate_anycast_password('ospf',enable_password)
        display_msg("PASS: Anycast enable password successfully validated")
        
        display_msg("---------Test Case 75 Execution Completed----------")


    @pytest.mark.run(order=76)
    def test_076_validate_anycast_ospf_ipv6_password_encryption_grid2(self):
        """
        Validate that the anycast password from the CLI show command is encrypted in grid2 after backup restore
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 76 Execution Started          |")
        display_msg("----------------------------------------------------")
        display_msg("Getting the actual password from ospf6d.conf file")
        password, enable_password = get_anycast_password('ospf6')
        if not password or not enable_password:
            display_msg("FAIL: Failed to fetch the password")
            assert False
        
        display_msg("Getting the encrypted password from CLI output")
        pswd, en_pswd = get_pswd_from_cli('ipv6_ospf')
        if not pswd or not en_pswd:
            display_msg("FAIL: Failed to fetch the password")
            assert False
        
        if password in pswd:
            display_msg("FAIL: CLI output of anycast password is not encrypted")
            assert False
        display_msg("PASS: CLI output of anycast password is encrypted")
        
        if enable_password in en_pswd:
            display_msg("FAIL: CLI output of anycast enable password is not encrypted")
            assert False
        display_msg("PASS: CLI output of anycast enable password is encrypted")
        
        validate_anycast_password('ospf6',password)
        display_msg("PASS: Anycast password successfully validated")
        
        validate_anycast_password('ospf6',enable_password)
        display_msg("PASS: Anycast enable password successfully validated")
        
        display_msg("---------Test Case 76 Execution Completed----------")

    @pytest.mark.run(order=77)
    def test_077_validate_anycast_bgp_ipv4_password_encryption_grid2(self):
        """
        Validate that the anycast password from the CLI show command is encrypted in grid2 after backup restore
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 77 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Getting the actual password from bgpd.conf file")
        password, enable_password = get_anycast_password('bgp')
        if not password or not enable_password:
            display_msg("FAIL: Failed to fetch the password")
            assert False
        
        display_msg("Getting the encrypted password from CLI output")
        pswd, en_pswd = get_pswd_from_cli('bgp')
        if not pswd or not en_pswd:
            display_msg("FAIL: Failed to fetch the password")
            assert False
        
        if password in pswd:
            display_msg("FAIL: CLI output of anycast password is not encrypted")
            assert False
        display_msg("PASS: CLI output of anycast password is encrypted")
        
        if enable_password in en_pswd:
            display_msg("FAIL: CLI output of anycast enable password is not encrypted")
            assert False
        display_msg("PASS: CLI output of anycast enable password is encrypted")
        
        validate_anycast_password('bgp',password)
        display_msg("PASS: Anycast password successfully validated")
        
        validate_anycast_password('bgp',enable_password)
        display_msg("PASS: Anycast enable password successfully validated")
        
        display_msg("---------Test Case 77 Execution Completed----------")


    @pytest.mark.run(order=78)
    def test_078_validate_anycast_bgp_ipv6_password_encryption_grid2(self):
        """
        Validate that the anycast password from the CLI show command is encrypted in grid2 after backup restore
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 78 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Getting the actual password from bgpd.conf file")
        password, enable_password = get_anycast_password('bgp')
        if not password or not enable_password:
            display_msg("FAIL: Failed to fetch the password")
            assert False
        
        display_msg("Getting the encrypted password from CLI output")
        pswd, en_pswd = get_pswd_from_cli('ipv6_bgp')
        if not pswd or not en_pswd:
            display_msg("FAIL: Failed to fetch the password")
            assert False
        
        if password in pswd:
            display_msg("FAIL: CLI output of anycast password is not encrypted")
            assert False
        display_msg("PASS: CLI output of anycast password is encrypted")
        
        if enable_password in en_pswd:
            display_msg("FAIL: CLI output of anycast enable password is not encrypted")
            assert False
        display_msg("PASS: CLI output of anycast enable password is encrypted")
        
        validate_anycast_password('bgp',password)
        display_msg("PASS: Anycast password successfully validated")
        
        validate_anycast_password('bgp',enable_password)
        display_msg("PASS: Anycast enable password successfully validated")
        
        display_msg("---------Test Case 78 Execution Completed----------")

# Cleanup
    
    @pytest.mark.skip
    def test_cleanup(self):
        """
        this is cleanup testcase
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case cleanup Execution Started     |")
        display_msg("----------------------------------------------------")
        display_msg("Cleanup")
        for grid in [config.grid_fqdn,config.grid_member1_fqdn]:
            display_msg("GRID: "+grid)
            add_listen_on_ip_addresses([],fqdn=grid)
            add_anycast_interface('',fqdn=grid)
            display_msg("Sleeping 5 minutes")
            sleep(300)
            configure_anycast_ospf('',fqdn=grid)
            configure_anycast_bgp('',fqdn=grid)

        
        

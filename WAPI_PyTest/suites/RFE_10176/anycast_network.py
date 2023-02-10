import ipaddress
import os
import subprocess
import pexpect
import sys
from time import sleep


#NETWORK = '10.34.7.0'

#vm_id = 'vm-10-77'

def fetch_network_details(NETWORK):
    try:
        os.system('source /import/tools/qa/bin/qaenv')
        stream = os.popen('get_lab_info -S '+NETWORK)
        output = stream.readlines()
        stream.close()
    except OSError as e:
        print("Unable to open a stream")
        print(e)
        assert False

    NETMASK = list(filter(lambda x: 'NETMASK'  in x, output))[0].split('=')[1].strip("\n")

    V6NETWORK = list(filter(lambda x: 'V6NETWORK'  in x, output))[0].split('=')[1].strip("\n")

    V6CIDR = list(filter(lambda x: 'V6CIDR'  in x, output))[0].split('=')[1].strip("\n")

    return NETMASK,V6NETWORK,V6CIDR



def fetch_non_pingable_IPv4_IPv6_ip_addresses(NETWORK,NETMASK,V6NETWORK,V6CIDR):

    test = ipaddress.ip_network(unicode(NETWORK+'/'+NETMASK))
    ipv4_addr=''
    for x in test.hosts():
        x_y= ipaddress.IPv4Address(x)+ 30
        try:
            return_code = subprocess.call(['ping','-c','8','-W','10',str(x_y)])
        except subprocess.CalledProcessError as e:
            print("Pinging the IP address failed")
            print(e)
            assert False
        if return_code != 0:
            ipv4_addr = str(x_y)
            break
    #print(ipv4_addr)


    test = ipaddress.ip_network(unicode(V6NETWORK+'/'+V6CIDR))
    ipv6_addr = ''
    for x in test.hosts():
        x_y= ipaddress.IPv6Address(x)+ 30
        try:
            return_code = subprocess.call(['ping6','-c','8','-W','10',str(x_y)])
        except subprocess.CalledProcessError as e:
            print("Pinging the IP address failed")
            print(e)
            assert False
        if return_code != 0:
            ipv6_addr = str(x_y)
            break
    #print(ipv6_addr)
    return ipv4_addr,ipv6_addr

        

def execute_netctl_command_on_the_anycast_client(vm_id,NETWORK):
    print("Executing netctl command")
    try:
        return_code = subprocess.call(['netctl_system','-i','lan','-a','vlanset','-H',vm_id,'-S',NETWORK])
    except subprocess.CalledProcessError as e:
        print("Execution of netctl_system failed")
        print(e)
        assert False
    if return_code == 0:
        print("netctl_system command execution successful on LAN1 for network "+NETWORK)
        return 0
    else:
        print("netctl_system command execution failed")
        assert False


def change_the_IPs_of_the_anycast_client_and_check_if_the_client_pings_with_new_IPs(vm_id,ipv4_addr,NETMASK,ipv6_addr,V6CIDR):
    print("Changing the IPv4 and IPv6 address of the eth1 interface on "+vm_id)
    try:
        child=pexpect.spawn("console_connect -H "+vm_id)
        child.expect(".*Escape character is .*",timeout=100)
        child.sendline("\r")
        login_required = child.expect(["bash-4.3#","login:"])
        if login_required == 1:
            child.sendline("root")
            child.expect("Password:")
            child.sendline("infoblox")
            child.expect("bash-4.3#")
            
        child.sendline("ifconfig eth1 "+ipv4_addr+" netmask "+NETMASK)
        child.expect("bash-4.3#")
        output = child.before
        error_list = ['unknown','error']
        if any(error in output.lower() for error in error_list):
            print("Error changing the eth1 IPv4 ip address, please refer the below output")
            print(output)
            assert False
        else:
            #child.sendline("ifconfig eth1 inet6 add "+ipv6_addr+"/"+V6CIDR)
            child.sendline("ip -6 addr add "+ipv6_addr+"/"+V6CIDR+" dev eth1")
            child.expect("bash-4.3#")
            output = child.before
            error_list = ['unknown','error']
            if any(error in output.lower() for error in error_list):
                print("Error changing the eth1 IPv6 ip address, please refer the below output")
                print(output)
                assert False
            else:
                sleep(10)
                child.sendline("ifconfig eth1")
                child.expect("bash-4.3#")
                output = child.before
                child.sendline("ifconfig eth1")
                child.expect("bash-4.3#")
                output = child.before
                print(output)
                if 'inet '+ipv4_addr+'  netmask '+NETMASK in output:
                    print("IPv4 address validation successful in ifconfig output")
                    assert True
                else:
                    print("IPv4 address validation failed in ifconfig output")
                    print('inet '+ipv4_addr+'  netmask '+NETMASK)
                    print(output)
                    assert False

                if 'inet6 '+ipv6_addr+'  prefixlen '+V6CIDR in output:
                    print("IPv6 address validation successful in ifconfig output")
                    assert True
                else:
                    print('inet6 '+ipv6_addr+'  prefixlen '+V6CIDR)
                    print("IPv6 address validation failed in ifconfig output")
                    print(repr(output))
                    assert False
    except pexpect.ExceptionPexpect as e:
        print("Failed to change the ips on the eth1 interface, check below output for error")
        print(e)
        assert False
    else:
        child.close()


    print("Check if the newly configured IPv4 and IPv6 address are pingable")

    print("Checking for the IPv4 address")

    try:
        return_code = subprocess.call(['ping','-c','8','-W','10',ipv4_addr])
        if return_code == 0:
            print("Ping to IPv4 address "+ipv4_addr+" successful")
        else:
            print("Ping to IPv4 address "+ipv4_addr+" unsuccessful")
            assert False
    except subprocess.CalledProcessError as e:
        print("Failed to perform ping operation, please check below output")
        print(e)
        assert False



    print("Checking for the IPv6 address")

    try:
        return_code = subprocess.call(['ping6','-c','8','-W','10',ipv6_addr])
        if return_code == 0:
            print("Ping to IPv6 address "+ipv6_addr+" successful")
        else:
            print("Ping to IPv6 address "+ipv6_addr+" unsuccessful")
            assert False
    except subprocess.CalledProcessError as e:
        print("Failed to perform ping operation, please check below output")
        print(e)
        assert False



#return ipv4_addr,ipv6_addr




def main():
    NETWORK = sys.argv[1]
    vm_id = sys.argv[2]

    NETMASK,V6NETWORK,V6CIDR = fetch_network_details(NETWORK)

    ipv4_addr,ipv6_addr = fetch_non_pingable_IPv4_IPv6_ip_addresses(NETWORK,NETMASK,V6NETWORK,V6CIDR) 

    execute_netctl_command_on_the_anycast_client(vm_id,NETWORK)

    change_the_IPs_of_the_anycast_client_and_check_if_the_client_pings_with_new_IPs(vm_id,ipv4_addr,NETMASK,ipv6_addr,V6CIDR)

    try:
        f = open("config.py","a")
        f.write('\nanycast_client=\"'+ipv4_addr+'\"\n')
        f.write('anycast_client_ipv6=\"'+ipv6_addr+'\"')
        f.close()
    except Exception as e:
        print("Unable to open config file for writing the anycast client details. PLease check below output for error")
        print(e)
        assert False
    return 0



if __name__ == "__main__":
    main()






    





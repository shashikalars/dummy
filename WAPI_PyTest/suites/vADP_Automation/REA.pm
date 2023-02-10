package REA;

# This provides most of the functional code to test SNORT Rules on a Trillion/Billian card.
# REA stands for Rules Engine Automation.  This allows for easy creation of many Perl programs
# to test different SNORT rules, but avoids duplicating this code in each of them.
#
# See the /import/tools/qa/tools/REA directory for examples, but a test suite can be as simple as
#   #!/usr/bin/perl
#   use lib "/import/tools/qa/tools/REA";
#   use REA;
#   my $ssh_ip=shift;
#   my $ip=shift;
#   my @SNORT_Rules=('drop udp any any -> any 53 (sid:1234; metadata:"Drop DNS Queries for foo.com."; content:"|03|foo|03|com|00|"; offset:12;)');
#   my @Test_Cases=({cmd=>"dig +retries=0 \@$ip foobar.com", rule=>''},
#                   {cmd=>"dig            \@$ip anything.foo.com", rule=>1234, count=>3});
#   my $test = REA->new(ssh_ip=>$ssh_ip, test_ip=>$ip, rules=>\@SNORT_Rules, test_cases=>\@Test_Cases);
#   unless ($test) {die "Could not configure test environment to $ip\n"}
#   $test->load_rules();
#   $test->execute_test_cases();
#   $test->evaluate();
#   $test->summarize();

use strict;
use warnings;
use diagnostics;

my $SSH_FLAGS="-q -o BatchMode=yes -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ServerAliveInterval=15";
my $my_hostname=`hostname`;
chomp $my_hostname;
my ($debug, $my_IP_address, $packet_count, $same_subnet);
my $myname="$0";
$myname=~s/.*\///;

my $rules_filename=$0;
$rules_filename=~s/.*\///;
my $rules_directory='/usr/bin/marvin/atp/IDS';
my $nios_filename = "$rules_directory/$rules_filename";
my $grid_master_ip;
my $Have_Not_Imported_Infoblox_PAPI_yet=1;
my %rule_tweaks;                          # The rule settings he wanted, which is a superset of
my %changed_rules;                        # The rule settings to be restored later.

sub new {
  my $class = shift;
  my %args = @_;
  my $self = \%args;
  bless $self, $class;

  my $cmd_output;
  my $addressing_mode;
  my $ping_command;

  my $test_case_number;

  if ($ENV{'DEBUG_REA'}) {$self->{debug}=1}

  ###############################################################################################
  #  Verify the SSH IP address, which we'll use to ssh different commands to NIOS.              #
  ###############################################################################################
  if ($self->{ssh_ip} !~ /^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$/ && $self->{ssh_ip} !~ /^[\da-f:]*$/) {
    die "The SSH IP address ($self->{ssh_ip}) does not look like an IP address.\n";
  }
  $grid_master_ip=$self->{ssh_ip};           # May get corrected later if this is grid member.

  ###############################################################################################
  #  Verify IP address of the device he wants me to test, by ensuring that I have a route to    #
  #  that IP address and while we're at it, learn which IP address I'll be using to get there.  #
  #  The output of the "ip route get $test_ip" command differs slightly depending on whether    #
  #  the client machine is on the same subnet as the test IP address or not.  When it's not     #
  #  on the same subnet (i.e. it has to go through the client's default gateway), it's          #
  #    10.35.1.132 via 10.34.82.1 dev eth1  src 10.34.82.2                                      #
  #  When it IS on the same subnet, there won't be that "via" clause.                           #
  ###############################################################################################
  if ($self->{test_ip} =~ /^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$/) {   # Are we testing IPv4 today?
    $self->{addressing_mode}='IPv4';
    $self->{ping_command}='ping';
    #$cmd_output=`ip r g $self->{test_ip}`;
    $cmd_output=`/usr/sbin/ip r g $self->{test_ip}`;
    if ($cmd_output !~ / src ([^ ]*) /) {
      die "You don't have routing to the $self->{test_ip} IP address.\n";
    }
    $self->{my_IP_address}=$1;
    if ($cmd_output =~ / via /) {$self->{same_subnet}=0}
                           else {$self->{same_subnet}=1}
  } elsif ($self->{test_ip} =~ /^[\da-f:]*$/) {                       # Or are we testing IPv6?
    $self->{addressing_mode}='IPv6';
    $self->{ping_command}='ping6';
    if (`/sbin/ifconfig` !~ /inet6 (.*)\d* Scope.*global/i) {
      die "Your system does not have an IPv6 address, so you can't send to an IPv6 address.\n";
    }
    $cmd_output=`ip -6 r g $self->{test_ip}`;
    if ($cmd_output !~ / src ([^ ]*) /) {
      die "You don't have routing to the $self->{test_ip} IPv6 address.\n";
    }
    $self->{my_IP_address}=$1;
    if ($cmd_output =~ / via /) {$self->{same_subnet}=0}
                           else {$self->{same_subnet}=1}
  } else {
    die "The IP address ($self->{test_ip}) does not look like an IP address.\n";
  }
  if ($self->{debug}) {print "Using $self->{addressing_mode} from my $self->{my_IP_address} IP address.\n"}

  ###############################################################################################
  #  Default to loose checking of the source IP address in the threat-protect-log lines.        #
  ###############################################################################################
  if (! defined($self->{strict_source_IP_checking})) {$self->{strict_source_IP_checking}=0}

  if (! $self->{rules} && ! $self->{rules_filename}) {die "You failed to provide any SNORT rules.\n"}

  if (defined($self->{rules_filename}) && $self->{rules_filename} ne '') {
    if ("$self->{rules_filename}" =~ /^NIOS:/ || "$self->{rules_filename}" eq 'NIOS') {
      if ("$self->{rules_filename}" eq 'NIOS:' ||
          "$self->{rules_filename}" eq 'NIOS') {$nios_filename = '/infoblox/var/atp_conf/rules.txt'}
      elsif ("$self->{rules_filename}" eq 'NIOS:me') {$nios_filename = "$rules_directory/$rules_filename"}
      elsif ("$self->{rules_filename}" =~ /^NIOS:(.+)$/) {$nios_filename = "$1"}
    }
  }

  ###############################################################################################
  #  Is the target machine online?  Wait 20 seconds if not, then die.                           #
  ###############################################################################################
  if ($self->{debug}) {print localtime() . ": Waiting for $self->{ssh_ip} to come online by pinging $self->{ssh_ip} from your machine ...\n"}
  my $start_time=time();            # Wait up to 30 seconds for the machine to answer pings.
  my $elapsed_time=0;
  while ($elapsed_time < 30) {
    `ping -nq -c 1 -W 2 $self->{ssh_ip}`;
    if ($? == 0) {last}

    $elapsed_time=time() - $start_time;
    if ($elapsed_time > 30) {
      print STDERR localtime() . ": waited too long for the $self->{ssh_ip} NIOS to come online.  Giving up.\n";
      exit 4;
    }

    print localtime() . ": still waiting for $self->{ssh_ip} to come online.  It's been $elapsed_time seconds so far ...\n";
    sleep 2;
  }
  $elapsed_time=time() - $start_time;
  if ($self->{debug}) {print localtime() . ": Machine is reachable on $self->{ssh_ip} after $elapsed_time seconds.\n"}

  ###############################################################################################
  #  Ensure I can ssh to the target machine.  Remedy if I can't.                                #
  #                                                                                             #
  #  Rick, can you recover from this error message and retry?                                   #
  #     Offending key in /mnt/home/rjasper/.ssh/known_hosts:1240                                #
  ###############################################################################################
  $cmd_output=`ssh $SSH_FLAGS root\@$self->{ssh_ip} ls -ld /infoblox 2>/dev/null`;
  if ($? == 0) {
    if ($self->{debug}) {print "    I can already ssh to $self->{ssh_ip}, so I don't have to use addkeys.\n"}
  } else {
    print "    Calling addkeys $self->{ssh_ip} ...\n";
    `addkeys $self->{ssh_ip}`;
    if ($? == 0) {
      system("/usr/bin/ssh $SSH_FLAGS root\@$self->{ssh_ip} date");
      if ($? == 0) {
        if ($self->{debug}) {print "    addkeys was successful.\n"}
      } else {
        die "addkeys apparently failed.  If not using the grid's VIP (usually LAN, but maybe MGMT), then you have to do the addkeys yourself first.\n";
      }
    } else {
      die "addkeys failed.  If not using the grid's VIP (usually LAN, but maybe MGMT), then you have to do the addkeys yourself first.\n";
    }
  }

  ###############################################################################################
  #  There's an SSH rate limiting rule in the NIOS firewall that REA now trips over.            #
  #  I believe this used to be 20 SSH sessions/minute, but now it's 10/minute.                  #
  ###############################################################################################
  $cmd_output=`ssh $SSH_FLAGS root\@$self->{ssh_ip} ls -l /infoblox/var/debug_ssh_enabled 2>/dev/null`;
  if ($cmd_output !~ /^-rw-rw-rw- .* \/infoblox\/var\/debug_ssh_enabled/) {
    system("/usr/bin/ssh $SSH_FLAGS root\@$self->{ssh_ip} touch /infoblox/var/debug_ssh_enabled");
    print localtime() . ": Restarting NIOS because I had to touch /infoblox/var/debug_ssh_enabled ...\n";
    system("/usr/bin/ssh $SSH_FLAGS root\@$self->{ssh_ip} /infoblox/rc restart 2>/dev/null");
    print localtime() . ": Waiting for $self->{ssh_ip} to come online after restarting product ...\n";

# Rick, there's got to be a better way to see when NIOS is again ready after a NIOS restart.  Just answering pings isn't enough.
    my $start_time=time();            # Wait up to 5 minutes for the machine to answer pings.
    my $elapsed_time=0;
    while ($elapsed_time < 300) {
      `ping -nq -c 1 -W 2 $self->{ssh_ip}`;
      if ($? == 0) {last}

      $elapsed_time=time() - $start_time;
      if ($elapsed_time > 300) {
        print STDERR localtime() . ": waited too long for the $self->{ssh_ip} NIOS to come online.  Giving up.\n";
        exit 4;
      }

      print localtime() . ": still waiting for $self->{ssh_ip} to come back after restart.  It's been $elapsed_time seconds so far ...\n";
      sleep 2;
    }

    $elapsed_time=time() - $start_time;
    if ($self->{debug}) {print localtime() . ": NIOS on $self->{ssh_ip} finally came back after $elapsed_time seconds.\n"}
    sleep 30;                                 # NIOS needs another few seconds to fully come back.
  }

  $cmd_output=`ssh $SSH_FLAGS root\@$self->{ssh_ip} grep CLIENT_VERSION= /infoblox/config 2>/dev/null`;
  if ($cmd_output =~ /CLIENT_VERSION=(.*)$/) {
    $self->{NIOS_version}=$1;
  } else {
    die "Could not determine NIOS version of $self->{ssh_ip}.  Command output was $cmd_output\n";
  }
  $self->{firmware_version}=`ssh $SSH_FLAGS root\@$self->{ssh_ip} /usr/bin/marvin/marvin_cli fw_version 2>/dev/null`;
  chomp $self->{firmware_version};

  $self->{hardware_id}=`ssh $SSH_FLAGS root\@$self->{ssh_ip} cat /infoblox/var/hw.txt 2>/dev/null`;
  chomp $self->{hardware_id};
  $cmd_output=`identify_lab_unit $self->{hardware_id}`;
  if ($cmd_output && $cmd_output =~ /$self->{hardware_id} is (.*)$/) {
    $self->{lab_id}=$1;
  } else {
    $self->{lab_id}='Unknown';
  }

  ###############################################################################################
  #  Ensure the root file system is mounted read-write.                                         #
  ###############################################################################################
  $cmd_output=`ssh $SSH_FLAGS root\@$self->{ssh_ip} mount 2>/dev/null | grep ' on / '`;
  if ($cmd_output =~ /ro,/) {
    if ($self->{debug}) {print "Have to mount the root file system read-write ...\n"}
    `ssh $SSH_FLAGS root\@$self->{ssh_ip} mount -oremount,rw / 2>/dev/null`;
  }

  ###############################################################################################
  #  If need be, copy over the atp_compile.sh program & ids.conf file.                          #
  ###############################################################################################
  $cmd_output=`ssh $SSH_FLAGS root\@$self->{ssh_ip} ls -l $rules_directory/atp_compile.sh 2>/dev/null`;
  if ($cmd_output !~ /^-rwx.*\/atp_compile\.sh/) {
    if (-f '/import/tools/qa/tools/REA/atp_compile.sh') {
      if ($self->{debug}) {print "Have to scp over /import/tools/qa/tools/REA/atp_compile.sh ...\n"}
      `scp $SSH_FLAGS -p /import/tools/qa/tools/REA/atp_compile.sh root\@$self->{ssh_ip}:/usr/bin/marvin/atp/IDS 2>/dev/null`;
    } else {
      die "What happened to /import/tools/qa/tools/REA/atp_compile.sh ??  I couldn't scp it to $self->{ssh_ip}\n";
    }
  }
  $cmd_output=`ssh $SSH_FLAGS root\@$self->{ssh_ip} ls -l $rules_directory/ids.conf 2>/dev/null`;
  if ($cmd_output !~ /^-rw.*\/ids.conf/) {
    if (-f '/import/tools/qa/tools/REA/ids.conf') {
      if ($self->{debug}) {print "Have to scp over /import/tools/qa/tools/REA/ids.conf ...\n"}
      `scp $SSH_FLAGS -p /import/tools/qa/tools/REA/ids.conf root\@$self->{ssh_ip}:/usr/bin/marvin/atp/IDS 2>/dev/null`;
    } else {
      die "What happened to /import/tools/qa/tools/REA/ids.conf ??  I couldn't scp it to $self->{ssh_ip}\n";
    }
  }

  ###############################################################################################
  #  Which network interface has the IP address I want to test?  This is to ensure that I       #
  #  have a defined IP address and to know which capture_interface to use if we're going to     #
  #  ask NIOS to do a traffic capture for us.                                                   #
  #                                                                                             #
  #  bond0 is used when doing NIC Teaming on the LAN and LAN2 interfaces.                       #
  #  lo is used when BGP or OSPF is defined for an IPv6 address.                                #
  #  lo:0 through lo:n is used when BGP or OSPF is defined for an IPv4 address.                 #
  #                                                                                             #
  # The different ifconfig command outputs are                                                  #
  # bond0     Link encap:Ethernet  HWaddr F4:87:71:00:06:29                                     #
  #           inet addr:10.34.9.51  Bcast:10.34.9.255  Mask:255.255.255.0                       #
  #           inet6 addr: 2620:10a:6000:2266::33/64 Scope:Global                                #
  #           inet6 addr: fe80::f687:71ff:fe00:629/64 Scope:Link                                #
  #           UP BROADCAST RUNNING MASTER MULTICAST  MTU:1500  Metric:1                         #
  #           RX packets:1284129 errors:0 dropped:8549 overruns:0 frame:0                       #
  #           TX packets:371380 errors:0 dropped:0 overruns:0 carrier:0                         #
  #           collisions:0 txqueuelen:0                                                         #
  #           RX bytes:818450519 (780.5 MiB)  TX bytes:0 (0.0 b)                                #
  # lo        Link encap:Local Loopback                                                         #
  #           inet addr:127.0.0.1  Mask:255.0.0.0                                               #
  #           inet6 addr: 2222::11/128 Scope:Global                                             #
  #           inet6 addr: ::1/128 Scope:Host                                                    #
  #           inet6 addr: 2222::13/128 Scope:Global                                             #
  #           inet6 addr: 2222::12/128 Scope:Global                                             #
  #           UP LOOPBACK RUNNING  MTU:16436  Metric:1                                          #
  #           RX packets:839294 errors:0 dropped:0 overruns:0 frame:0                           #
  #           TX packets:839294 errors:0 dropped:0 overruns:0 carrier:0                         #
  #           collisions:0 txqueuelen:0                                                         #
  #           RX bytes:295084142 (281.4 MiB)  TX bytes:295084142 (281.4 MiB)                    #
  #                                                                                             #
  # lo:1      Link encap:Local Loopback                                                         #
  #           inet addr:22.22.22.12  Mask:255.255.255.255                                       #
  #           UP LOOPBACK RUNNING  MTU:16436  Metric:1                                          #
  #                                                                                             #
  # lo:2      Link encap:Local Loopback                                                         #
  #           inet addr:22.22.22.13  Mask:255.255.255.255                                       #
  #           UP LOOPBACK RUNNING  MTU:16436  Metric:1                                          #
  #                                                                                             #
  # lo:3      Link encap:Local Loopback                                                         #
  #           inet addr:22.22.22.11  Mask:255.255.255.255                                       #
  #           UP LOOPBACK RUNNING  MTU:16436  Metric:1                                          #
  #                                                                                             #
  # oct1      Link encap:Ethernet  HWaddr F4:87:71:00:05:5D                                     #
  #           inet addr:10.35.2.40  Bcast:10.35.255.255  Mask:255.255.0.0                       #
  #           inet6 addr: 2620:10a:6000:2400::228/64 Scope:Global                               #
  #           inet6 addr: fe80::f687:71ff:fe00:55d/64 Scope:Link                                #
  #           UP BROADCAST RUNNING MULTICAST  MTU:1500  Metric:1                                #
  #           RX packets:11087650 errors:0 dropped:145 overruns:0 frame:0                       #
  #           TX packets:410477 errors:0 dropped:0 overruns:0 carrier:0                         #
  #           collisions:0 txqueuelen:1000                                                      #
  #           RX bytes:702990418 (670.4 MiB)  TX bytes:0 (0.0 b)                                #
  ###############################################################################################
  my $ifconfig_output=`ssh $SSH_FLAGS root\@$self->{ssh_ip} ifconfig 2>/dev/null`;
  my $interface;
  while ($ifconfig_output =~ /([^\n]*)?\n/g) {
    my $line=$1;
    if ($line =~ /^([^ ]+) /) {
      $interface=$1;
    } elsif ($line =~ /^ *inet addr:$self->{test_ip} /) {
      $self->{interface} = $interface;
      last;
    } elsif ($line =~ /^ *inet6 addr: $self->{test_ip}\/\d/) {
      $self->{interface} = $interface;
      last;
    }
  }
  if (! $self->{interface}) {die "Could not find $self->{test_ip} on any of NIOS's network interfaces.\n"}

  ###############################################################################################
  # What is the MGMT, LAN, and LAN2 interfaces for this hardware platform?  Unfortunately,      #
  # there is no consistent interface name mapping, so we have to query NIOS.                    #
  #                                                                                             #
  # I don't know if 'ANY' is right for an OSPF loopback IP address, or if 'BOND' works, or      #
  # if this works for IPv6.  I suppose I should test all of those.                              #
  ###############################################################################################
  $self->{capture_interface}='ANY';             # Default if this loop fails to find it.
  for ('PUBLIC', 'LAN2', 'HA', 'BOND', 'MGMT') {
    my $ci = `ssh $SSH_FLAGS root\@$self->{ssh_ip} /infoblox/common/bin/platform_query_device_info -d ${_}_INTERFACE -o all 2>/dev/null | cut -f2 -d' '`;
    chomp $ci;
    if ($self->{interface} eq $ci) {
      if ($_ eq 'PUBLIC') {$self->{capture_interface}='LAN'}
                     else {$self->{capture_interface}=$_}
      last;
    }
  }

  ###############################################################################################
  #  Is the test IP address online?  Wait 20 seconds if not, then die.                          #
  ###############################################################################################
  if ($self->{debug}) {print localtime() . ": Waiting for $self->{test_ip} to come online by pinging $self->{test_ip} from your machine ...\n"}
  $start_time=time();            # Wait up to 30 seconds for the machine to answer pings.
  $elapsed_time=0;
  while ($elapsed_time < 30) {
    `$self->{ping_command} -nq -c 1 -W 2 $self->{test_ip}`;
    if ($? == 0) {last}

    $elapsed_time=time() - $start_time;
    if ($elapsed_time > 30) {
      print STDERR localtime() . ": waited too long for the $self->{test_ip} NIOS to come online.  Giving up.\n";
      exit 4;
    }

    print localtime() . ": still waiting for $self->{test_ip} to come online.  It's been $elapsed_time seconds so far ...\n";
    sleep 2;
  }
  $elapsed_time=time() - $start_time;
  if ($self->{debug}) {print localtime() . ": Machine is reachable on $self->{test_ip} after $elapsed_time seconds.\n"}

  if (! $self->{skip_DNS_prereq_checks}) {
    #############################################################################################
    #  Verify named is configured correctly to point to a REA_dns name server.                  #
    #  If not, see if we can tell him what's wrong.                                             #
    #    - listening on our IP address,                                                         #
    #    - have a forwarder defined,                                                            #
    #    - the "Use Forwarders Only" checkbox is checked,                                       #
    #    - allows recursive queries,                                                            #
    #    - answers a special REA_dns query of 003X69REA.pm.test TXT.                            #
    #############################################################################################
    #sleep 6;
    sleep 600;
    #my $dig_cmd_output=`dig +short +tries=1 +time=0 \@$self->{test_ip} 003X69.REA.pm.test txt`;
    my $dig_cmd_output=`dig +short +tries=1 +time=0 \@$self->{test_ip} 130X69.REA.pm.test txt`;
    # We expect back "Response would be too long"
    print "QUERYING NIOS DIRECTLY AND CAPTUING OUTPUT - $dig_cmd_output\n";
    if ($dig_cmd_output !~ /^"Response would be too long"/) {
      print STDERR "A test \"dig +short +tries=1 +time=0 \@$self->{test_ip} 003X69.REA.pm.test txt\" command failed.\n";
      my $detail=0;

      # Let's see if we can figure out what's wrong.  Is named running on the NIOS box?
      $cmd_output=`ssh $SSH_FLAGS root\@$self->{ssh_ip} ps -ef 2>/dev/null | grep /usr/sbin/named | grep -v grep`;
      print "CHECKING WHETHER NAMED IS RUNNING $cmd_output\n";
      print "-------------------------";
      if ($cmd_output !~ '/usr/sbin/named') {
        print STDERR "   You don't have named running on $self->{test_ip}.\n";
        $detail=1;
      }
      # Look for the "forward only;" and "forwarders { 10.35.0.160; };" lines in the options section.
      $cmd_output=`ssh $SSH_FLAGS root\@$self->{ssh_ip} grep -B 222 -m 1 '\"^}\\;\"' /storage/infoblox.var/named_conf/named.conf 2>/dev/null | grep forward`;
      print "FORWARDER OUTPUT - $cmd_output\n";
      if ($cmd_output !~ /forward only;/) {
        print STDERR "   You need to check the \"Use Forwarders Only\" box under the Forwarders tab in DNS properties.\n";
        $detail=1;
      }
      if ($cmd_output !~ /forwarders \{ (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3});/) {
        print STDERR "   You need to define a DNS forwarder to a REA_dns server.\n";
        $detail=1;
      } else {                  # Confirm our forwarder is answering DNS requests.
        my $forwarder=$1;
        #$dig_cmd_output=`dig +short +tries=1 +time=0 \@$forwarder 003X69.REA.pm.test txt`;
        $dig_cmd_output=`dig +short +tries=1 +time=0 \@$forwarder 130X69.REA.pm.test txt`; 
        print "QUERYING DIRECTLY FORWARDER - $dig_cmd_output\n";
        if ($dig_cmd_output =~ /connection timed out; no servers could be reached/) {
          print STDERR "   You don't have any name server running on your $forwarder forwarder.\n";
          print STDERR "   In order to test the response rules, you need to use /import/tools/qa/tools/REA/REA_dns.\n";
          $detail=1;
        } elsif ($dig_cmd_output !~ /"Response would be too long"/) {
          print STDERR "   Some other wdns or wl program is running on your $forwarder forwarder, not REA_dns.\n";
          print STDERR "   In order to test the response rules, you need to use /import/tools/qa/tools/REA/REA_dns.\n";
          $detail=1;
        }
      }

      $cmd_output=`ssh $SSH_FLAGS root\@$self->{ssh_ip} grep listen-on /storage/infoblox.var/named_conf/named.conf 2>/dev/null`;
      if ($cmd_output !~ /listen-on.* $self->{test_ip}/) {
        print STDERR "   You don't have named listening on $self->{test_ip}\n";
        $detail=1;
      }

      $cmd_output=`ssh $SSH_FLAGS root\@$self->{ssh_ip} grep 'recursion yes' /storage/infoblox.var/named_conf/named.conf 2>/dev/null`;
      if ($cmd_output !~ /recursion/) {
        print STDERR "   You don't have recursive queries enabled.\n";
        $detail=1;
      }

      if (! $detail) {
        print STDERR "   I don't know why.  named is running & seems properly configured (listening on $self->{test_ip}, Recursion enabled, a Forwarder configured), the Forwarder itself is answering queries, but Queries to $self->{test_ip} are either not getting through or the Responses not getting back.  If you recently changed your DNS configuration, try flushing the DNS cache.";
        $detail=1;
      }

      exit 1;
    }
  } else {
    if ($self->{debug}) {print "Skipping DNS verification as requested.\n"}
  }

  ###############################################################################################
  #  Validate any test cases given to us.  Test cases are optional for when somebody just       #
  #  wants to load a set of SNORT rules and not execute any test cases.                         #
  ###############################################################################################
  if (defined($self->{test_cases}) && $self->{test_cases}) {
    $self->{Total_Test_Cases}=@{$self->{test_cases}};
  } else {
    $self->{Total_Test_Cases}=0;
  }
  return($self);
}

#################################################################################################
#  Read through the rules we have loaded and the test cases we're testing to see what's what.   #
#  This code used to be up in the new subroutine, but that was premature in the case where we   #
#  had to first enable the rule.                                                                #
#    - Remember whether a rule is an ALERT rule or a DROP rule so that we know what is          #
#      expected when the test case has just "rule=>130000700" or "count=10".                    #
#    - Remember any enable_condition a rule is predicated on.  For example, if we had a test    #
#      case for rule 100100100, which allows incoming Ipv4 Notify DNS packets, but that rule    #
#      didn't exist in the NIOS rules file, it's likely because this grid member does not       #
#      allow incoming zone transfers (IsMemberServiceDNSAllowIncomingZoneXferResponseIPv4).     #
#    - Initialize each test case's ending status to UNCHECKED.                                  #
#    - Skip any test case that references a rule that doesn't exist.                            #
#################################################################################################
sub review_rules_and_test_cases {
  my $self = shift;
  my %AUTO_Condition;
  my $AUTO_Conditions=`ssh $SSH_FLAGS root\@$self->{ssh_ip} egrep "'^[1-9][0-9][0-9][0-9][0-9]|^Is|^!Is'" /infoblox/var/atp_conf/last_published_rules_info.txt 2>/dev/null`;
  my $last_SID;
  while ($AUTO_Conditions =~ /([^\n]*)?\n/g) {
    my $line=$1;
       if ($line =~ /^(\d+)/) {$last_SID=$1}
    elsif ($line =~ /^(!?Is.*)/) {$AUTO_Condition{$last_SID}=$1}
  }

  ###############################################################################################
  #  If given a rules filename instead of the ruleset, then read the rules from there and       #
  #  stuff them into our rules array, comments, blank lines, and all.                           #
  #                                                                                             #
  #  If the rules filename starts with "NIOS:" then we'll get the rules off the NIOS box.       #
  #  If just "NIOS" or "NIOS:", then read /infoblox/var/atp_conf/rules.txt.                     #
  #  If just "NIOS:me", then read $rules_directory/$rules_filename.                             #
  #  If "NIOS:/anything/else", then presume /anything/else is a fully-qualified filename.       #
  ###############################################################################################
  if (defined($self->{rules_filename}) && $self->{rules_filename} ne '') {
    if ("$self->{rules_filename}" =~ /^NIOS:/ || "$self->{rules_filename}" eq 'NIOS') {
      if ("$self->{rules_filename}" eq 'NIOS:' || "$self->{rules_filename}" eq 'NIOS') {
        $self->{rules_version} = `ssh $SSH_FLAGS root\@$self->{ssh_ip} grep ^2 /infoblox/var/atp_conf/last_published_rules_info.txt 2>/dev/null | head -1`;
        chomp $self->{rules_version};
      }

      my $cmd_output=`ssh $SSH_FLAGS root\@$self->{ssh_ip} ls -l $nios_filename 2>/dev/null`;
      if ($cmd_output !~ /^-r.*$nios_filename/) {die "$nios_filename does not exist on the $self->{ssh_ip} NIOS box.  Can't read rules file.\n"}
      @{$self->{rules}}=`ssh $SSH_FLAGS root\@$self->{ssh_ip} cat $nios_filename 2>/dev/null`;
    } else {
      if (-r "$self->{rules_filename}") {
        open(FILE, "<$self->{rules_filename}") || die "Couldn't open $self->{rules_filename}\n";
        my @all_rules = <FILE>;
        close FILE;
        $self->{rules} = \@all_rules;
      } else {
        die "File $self->{rules_filename} does not exist or is not readable.\n";
      }
    }
  }

  ###############################################################################################
  #  Categorize each rule as alert or drop or pass rules.                                       #
  ###############################################################################################
  foreach my $rule (@{$self->{rules}}) {
       if ($rule =~ /^\s*alert\s.*\s*sid:\s*(\d*)/i) {$self->{rule_type}{$1} = 'ALERT'}
    elsif ($rule =~ /^\s*drop\s.*\s*sid:\s*(\d*)/i ) {$self->{rule_type}{$1} = 'DROP'}
    elsif ($rule =~ /^\s*pass\s.*\s*sid:\s*(\d*)/i ) {$self->{rule_type}{$1} = 'PASS'}
  }

  #############################################################################################
  #  If it's the normal case of test cases being passed to us, then loop through each         #
  #  test case to verify the commands, expected rules triggered, and initialize any other     #
  #  our test case variables.                                                                 #
  #############################################################################################
  for (my $test_case_index=0; $test_case_index<$self->{Total_Test_Cases}; $test_case_index++) {
    my $test_case_number=$test_case_index+1;

    # Initialize this test case's ending status.
    $self->{test_cases}[$test_case_index]{Status} = 'UNCHECKED';
    $self->{test_cases}[$test_case_index]{Reason} = '';

    ###########################################################################################
    #  Rick, you might want to enhance the REA framework to allow 'cmds' as well as 'cmd'.    #
    #  You can do almost the same kind of mapping of 'cmd' to 'cmds' as you do for            #
    #  rule/rules below, except cmds would need to be an array because you'll care about      #
    #  order (rules is a hash).  This would allow for the original                            #
    #     cmd=>'...', repeat=>n, delay=>n                                                     #
    #  or the more complicated cmds=>[{cmd=>'first  command', repeat=>n, delay=>n},           #
    #                                 {cmd=>'second command', repeat=>n, delay=>n},           #
    #                                 {cmd=>'third  command', repeat=>n, delay=>n},           #
    #                                 {cmd=>'fourth command', repeat=>n, delay=>n},           #
    #                                ]                                                        #
    ###########################################################################################


    ###########################################################################################
    #  The original 'rule' syntax allowed one to declare that this test case is either        #
    #    - not expected to trigger any rule (e.g. rule=>''), or                               #
    #    - expected to trigger exactly one rule exactly once (e.g. rule=>5001002).            #
    #                                                                                         #
    #  As we later learned, this was inadequate.  A test case can trigger multiple alert      #
    #  or drop rules, so we developed a more complicated 'rules' syntax.  Note the plural     #
    #  'rules' as contrasted to the singular 'rule' originally.  We also allow a 'count'      #
    #  or 'alert_count' or 'drop_count' to each rule.  We also backported the 3 count         #
    #  variables to the singular 'rules'.                                                     #
    #                                                                                         #
    #  If 'rules' was used for this test case, then it points to a hash of rules, keyed by    #
    #  their SID, that are expected to trigger a certain number of times, which can be        #
    #  specified with either count, alert_count, and/or drop_count.  For example,             #
    #    rules=>{5001111 => {count=>10},                                                      #
    #            5002222 => {alert_count=>4, drop_count=>3}},                                 #
    #  would say we expect 10 hits on rule 5001111 (alerts if that rule is an alert rule,     #
    #  else drops if that rule is a drop rule), as well as 4 alerts and 3 drops for rule      #
    #  5002222.                                                                               #
    #                                                                                         #
    #  Here, we map the old 'rule' syntax (if specified) into the new 'rules' syntax, so      #
    #  rule=>''      becomes $self->{test_cases}[$test_case_index]{rules}={} and              #
    #  rule=>5001002 becomes $self->{test_cases}[$test_case_index]{rules}{5001002}{count}=1   #
    #                                                                                         #
    #  After this loop, we'll never reference the old 'rule' syntax.                          #
    ###########################################################################################
    if (defined($self->{test_cases}[$test_case_index]{rule}) && defined($self->{test_cases}[$test_case_index]{rules})) {
      die "Your test case # $test_case_number has both 'rule' and 'rules'.  Use one or the other, not both.\n";
    }

    if (defined($self->{test_cases}[$test_case_index]{rule})) {       # Is this the old 'rule' syntax?
      if ($self->{test_cases}[$test_case_index]{rule}) {              # Positive test case where rule SID was given.
        if (defined($self->{test_cases}[$test_case_index]{count})) {          #  If count given, shouldn't have alert_count or drop_count.
          if (defined($self->{test_cases}[$test_case_index]{alert_count})) {
            die "Your test case # $test_case_number has both 'count' and 'alert_count'.  Use one or the other, not both.\n";
          }
          if (defined($self->{test_cases}[$test_case_index]{drop_count})) {
            die "Your test case # $test_case_number has both 'count' and 'drop_count'.  Use one or the other, not both.\n";
          }
          $self->{test_cases}[$test_case_index]{rules}{$self->{test_cases}[$test_case_index]{rule}}={count=>$self->{test_cases}[$test_case_index]{count}};
        } else {                                                              #  count was not given.  If alert_count and drop_count are also missing,
          if (! defined($self->{test_cases}[$test_case_index]{alert_count}) &&
              ! defined($self->{test_cases}[$test_case_index]{drop_count})) {
            $self->{test_cases}[$test_case_index]{rules}{$self->{test_cases}[$test_case_index]{rule}}{count}=1;   # then default to count=1.
          } else {
            if (defined($self->{test_cases}[$test_case_index]{alert_count})) {
              $self->{test_cases}[$test_case_index]{rules}{$self->{test_cases}[$test_case_index]{rule}}{alert_count}=$self->{test_cases}[$test_case_index]{alert_count};
            }
            if (defined($self->{test_cases}[$test_case_index]{drop_count})) {
              $self->{test_cases}[$test_case_index]{rules}{$self->{test_cases}[$test_case_index]{rule}}{drop_count}=$self->{test_cases}[$test_case_index]{drop_count};
            }
          }
        }
      } else {                                                        # Negative test case where rule SID was not given.
        if (defined($self->{test_cases}[$test_case_index]{count})) {
          die "Your test case # $test_case_number should not be using 'count' with a null SID.\n";
        }
        if (defined($self->{test_cases}[$test_case_index]{alert_count})) {
          die "Your test case # $test_case_number should not be using 'alert_count' with a null SID.\n";
        }
        if (defined($self->{test_cases}[$test_case_index]{drop_count})) {
          die "Your test case # $test_case_number should not be using 'drop_count' with a null SID.\n";
        }
        $self->{test_cases}[$test_case_index]{rules}={};
      }
    }

    ###########################################################################################
    # Go through each test case                                                               #
    #   - defaulting to count=1 if no counts were given, and                                  #
    #   - resolving any counts to either alert_count or drop_count depending on whether the   #
    #     referenced rule is an alert or a drop rule.                                         #
    #                                                                                         #
    # After this point, we'll never reference 'count', only 'alert_count' and 'drop_count'.   #
    ###########################################################################################
    if (%{$self->{test_cases}[$test_case_index]{rules}}) {
      foreach my $sid (keys %{$self->{test_cases}[$test_case_index]{rules}}) {

        if (defined($self->{test_cases}[$test_case_index]{skip_if_not_on_same_subnet}) &&
                    $self->{test_cases}[$test_case_index]{skip_if_not_on_same_subnet}==1 &&
                    $self->{same_subnet}==0) {
          print STDERR "Test case # $test_case_number will be skipped because this machine is not on the same subnet as your test IP ($self->{test_ip}).\n";
          $self->{test_cases}[$test_case_index]{Status} = 'SKIP';
          $self->{test_cases}[$test_case_index]{Reason} = "This machine is not on the same subnet as $self->{test_ip}.";
        } else {
          # If no count was given, default to count=1.
          if (! defined($self->{test_cases}[$test_case_index]{rules}{$sid}{count}) &&
              ! defined($self->{test_cases}[$test_case_index]{rules}{$sid}{alert_count}) &&
              ! defined($self->{test_cases}[$test_case_index]{rules}{$sid}{drop_count})) {$self->{test_cases}[$test_case_index]{rules}{$sid}{count}=1}

          # If count was given, set alert_count or drop_count depending on rule type.
          if (defined($self->{test_cases}[$test_case_index]{rules}{$sid}{count})) {
            if (defined($self->{rule_type}{$sid})) {
              if ($self->{rule_type}{$sid} eq 'ALERT') {
                $self->{test_cases}[$test_case_index]{rules}{$sid}={alert_count=>$self->{test_cases}[$test_case_index]{rules}{$sid}{count},drop_count=>0};
              } elsif ($self->{rule_type}{$sid} eq 'DROP') {
                $self->{test_cases}[$test_case_index]{rules}{$sid}={alert_count=>0,drop_count=>$self->{test_cases}[$test_case_index]{rules}{$sid}{count}};
              } else {
                print STDERR "Test case # $test_case_number references rule $sid, but it's not an ALERT or DROP rule.\n";
                $self->{test_cases}[$test_case_index]{rules}{$sid}={alert_count=>1, drop_count=>0};
              }
            } else {
              ###################################################################################
              # This test case references a rule that doesn't exist, so it'll be skipped.       #
              # If this rule has an Auto Condition, then that's probably why it is missing.     #
              # But sometimes it due to the HFA rules engine version, e.g. rule 200000001       #
              # won't be there for HFA engine versions < 3.                                     #
              ###################################################################################
              if (defined($AUTO_Condition{$sid})) {
                print STDERR "Test case # $test_case_number references rule $sid, but that rule isn't enabled because its $AUTO_Condition{$sid} AUTO condition is false.  This test case will not be run.\n";
                $self->{test_cases}[$test_case_index]{Status} = 'SKIP';
                $self->{test_cases}[$test_case_index]{Reason} = "$sid Rule's $AUTO_Condition{$sid} AUTO condition is false.";
              } else {
                print STDERR "Test case # $test_case_number references rule $sid, but that rule doesn't exist.  This test case will not be run.\n";
                $self->{test_cases}[$test_case_index]{Status} = 'SKIP';
                $self->{test_cases}[$test_case_index]{Reason} = "Rule $sid is missing.";
              }
            }
          } else {
            if ((defined($self->{test_cases}[$test_case_index]{rules}{$sid}{alert_count}) && ! defined($self->{rule_type}{$sid})) ||
                (defined($self->{test_cases}[$test_case_index]{rules}{$sid}{drop_count }) && ! defined($self->{rule_type}{$sid}))) {
              if (defined($AUTO_Condition{$sid})) {
                print STDERR "Test case # $test_case_number references rule $sid, but that rule isn't enabled because its $AUTO_Condition{$sid} AUTO condition is false.  This test case will not be run.\n";
                $self->{test_cases}[$test_case_index]{Status} = 'SKIP';
                $self->{test_cases}[$test_case_index]{Reason} = "$sid Rule's $AUTO_Condition{$sid} AUTO condition is false.";
              } else {
                print STDERR "Test case # $test_case_number references rule $sid, but that rule doesn't exist.  This test case will not be run.\n";
                $self->{test_cases}[$test_case_index]{Status} = 'SKIP';
                $self->{test_cases}[$test_case_index]{Reason} = "Rule $sid is missing.";
              }
            }
          }

          # Default any unset count fields to 0.
          if (! defined($self->{test_cases}[$test_case_index]{rules}{$sid}{alert_count})) {$self->{test_cases}[$test_case_index]{rules}{$sid}{alert_count}=0}
          if (! defined($self->{test_cases}[$test_case_index]{rules}{$sid}{drop_count})) {$self->{test_cases}[$test_case_index]{rules}{$sid}{drop_count}=0}
        }
      }
    }
  }
}

#################################################################################################
# If this test case is getting driven by our own set of rules, then load them onto the card.    #
# This was a lot more common in the early days, but nowadays, we mostly use whatever rules are  #
# already loaded onto NIOS.                                                                     #
#################################################################################################
sub load_rules {
  my $self = shift;
  my $cmd_output;

  $cmd_output=`ssh $SSH_FLAGS root\@$self->{ssh_ip} ls -l /infoblox/var/atp_backdoor 2>/dev/null`;
  if ($cmd_output !~ /^-rw-rw-rw- .* \/infoblox\/var\/atp_backdoor/) {
    system("/usr/bin/ssh $SSH_FLAGS root\@$self->{ssh_ip} touch /infoblox/var/atp_backdoor /infoblox/var/debug");
    print localtime() . ": Restarting NIOS because I had to touch /infoblox/var/atp_backdoor ...\n";
    system("/usr/bin/ssh $SSH_FLAGS root\@$self->{ssh_ip} /infoblox/rc restart 2>/dev/null");
    print localtime() . ": Waiting for $self->{ssh_ip} to come online after restarting product ...\n";

# Rick, there's got to be a better way to see when NIOS is again ready after a NIOS restart.  Just answering pings isn't enough.
    my $start_time=time();            # Wait up to 5 minutes for the machine to answer pings.
    my $elapsed_time=0;
    while ($elapsed_time < 300) {
      `ping -nq -c 1 -W 2 $self->{ssh_ip}`;
      if ($? == 0) {last}

      $elapsed_time=time() - $start_time;
      if ($elapsed_time > 300) {
        print STDERR localtime() . ": waited too long for the $self->{ssh_ip} NIOS to come online.  Giving up.\n";
        exit 4;
      }

      print localtime() . ": still waiting for $self->{ssh_ip} to come back after restart.  It's been $elapsed_time seconds so far ...\n";
      sleep 2;
    }

    $elapsed_time=time() - $start_time;
    if ($self->{debug}) {print localtime() . ": NIOS on $self->{ssh_ip} never came back after $elapsed_time seconds.\n"}
    sleep 5;                                  # NIOS needs another few seconds to fully come back.
  }

  ###############################################################################################
  #  If need be, load our SNORT rules we want to test onto the appliance.                       #
  ###############################################################################################
  if (defined($self->{rules_filename}) && ("$self->{rules_filename}" =~ /^NIOS:/ || "$self->{rules_filename}" eq 'NIOS')) {
    if ($self->{debug}) {print "The rules are already on NIOS at $nios_filename ...\n"}
  } else {
    $cmd_output=`ssh $SSH_FLAGS root\@$self->{ssh_ip} ls -l $rules_directory/$rules_filename 2>/dev/null`;
    if ($cmd_output =~ /^-rw.*\/$rules_filename/) {
      if ($self->{debug}) {print "Have to erase an old $rules_directory/$rules_filename ...\n"}
      `ssh $SSH_FLAGS root\@$self->{ssh_ip} rm $rules_directory/$rules_filename 2>/dev/null`;
    }

    open(RULES,">/tmp/$rules_filename.$$") || die "Could not open temporary file /tmp/$rules_filename.$$\n";
    foreach my $rule (@{$self->{rules}}) {
      print RULES "$rule\n";
    }
    close RULES;

    if ($self->{debug}) {print "scp-ing the rules over ...\n"}
    `scp $SSH_FLAGS /tmp/$rules_filename.$$ root\@$self->{ssh_ip}:$rules_directory/$rules_filename 2>/dev/null`;
    unlink("/tmp/$rules_filename.$$");
  }

  ###############################################################################################
  #  Compile the SNORT rules and turn bypass_tdpi off on the card.  These commands are          #
  #    cd /usr/bin/marvin/atp/IDS                                                               #
  #    ./atp_compile.sh /usr/bin/marvin/atp/IDS/ids.conf $nios_filename                         #
  #    /usr/bin/marvin/marvin_cli bypass_tdpi=false                                             #
  ###############################################################################################
  if ($self->{debug}) {print "Doing `ssh $SSH_FLAGS root\@$self->{ssh_ip} 'cd $rules_directory;./atp_compile.sh $rules_directory/ids.conf $nios_filename'`\n"}
  $cmd_output=`ssh $SSH_FLAGS root\@$self->{ssh_ip} 'cd $rules_directory;./atp_compile.sh $rules_directory/ids.conf $nios_filename'`;
  if ($self->{debug}) {print "The atp_compile program returned >$cmd_output< ...\n"}
  if ($cmd_output =~ /^((?:ERROR:|Undefined) .*)$/m) {
    print "There was an error compiling your rules: $1\n";
    exit 123;
  }

  if ($self->{debug}) {print "Doing `ssh $SSH_FLAGS root\@$self->{ssh_ip} '/usr/bin/marvin/marvin_cli bypass_tdpi=false'`\n"}
  `ssh $SSH_FLAGS root\@$self->{ssh_ip} '/usr/bin/marvin/marvin_cli bypass_tdpi=false 2>/dev/null 2>/dev/null'`;
}

###################################################################################################################################################
# Given a hash of rule SID's and the desired rule settings, connect to the grid master using                                                      #
# the Infoblox Perl API (downloading it if needed), and for each SID, ensure that rule is                                                         #
# enabled and it has the specified variable settings.                                                                                             #
# Remember if we change anything so we can restore this rule's settings later.                                                                    #
#                                                                                                                                                 #
# For the simple case of changing one rule as in Serve_Fail.response,                                                                             #
#   $test->tweak_rule_settings(200000003=>{PACKETS_PER_SECOND=>400, DROP_INTERVAL=>5, EVENTS_PER_SECOND=>3, RATE_ALGORITHM=>'Rate_Limiting'});    #
# For to check on and perhaps modify multiple rules as in BAT,                                                                                    #
#   $test->tweak_rule_settings(200000001=>{PACKETS_PER_SECOND=>400, DROP_INTERVAL=>5, EVENTS_PER_SECOND=>3, RATE_ALGORITHM=>'Rate_Limiting'},     #
#                              200000002=>{PACKETS_PER_SECOND=>400, DROP_INTERVAL=>5, EVENTS_PER_SECOND=>3, RATE_ALGORITHM=>'Rate_Limiting'},     #
#                              200000003=>{PACKETS_PER_SECOND=>400, DROP_INTERVAL=>5, EVENTS_PER_SECOND=>3, RATE_ALGORITHM=>'Rate_Limiting'});    #
###################################################################################################################################################
sub tweak_rule_settings {
  my $self = shift;
  my %rules_to_tweak = @_;
  my ($session, $rule, $config, $something_changed);
  my $publish=0;

  $self->get_and_import_Infoblox_PAPI();

  #############################################################################################
  # Connect to the grid master, redirecting to the grid master if this is a grid member.      #
  #############################################################################################
  $session = Infoblox::Session->new('master'=>$grid_master_ip, 'username'=>'admin', 'password'=>'infoblox');
  if (ref($session) ne 'Infoblox::Session') {die "Failed to create session to $grid_master_ip\n"}
  my $return_code = $session->status_code();
  my $response = $session->status_detail();
  if ($return_code != 0) {
    if ($response =~ /This server \(.*\) is not a grid master. The current grid master is: \[?([0-9a-f\.:]*)\]?/i) {
      my $new_grid_master_ip=$1;
      my $master_addressing_mode;
      if ($new_grid_master_ip =~ /^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/) {
        $master_addressing_mode='4';
      } elsif ($new_grid_master_ip =~ /^[a-fA-f0-9]{1,4}:[a-fA-f0-9:]*$/) {
        $master_addressing_mode='6';
      }
      $grid_master_ip=$new_grid_master_ip;                  # Silently follow the redirect
      $session = Infoblox::Session->new('master'=>$grid_master_ip, 'username'=>'admin', 'password'=>'infoblox');
      $return_code = $session->status_code();
      $response = $session->status_detail();
    } else {die "Failed to connect to the $grid_master_ip grid master.  return_code=$return_code and response=$response.\n"}
  }
  if (ref($session) ne 'Infoblox::Session') {die "$myname failed to get Infoblox::Session.\n"}

  foreach my $SID (keys %rules_to_tweak) {
    my %rule_settings = %{$rules_to_tweak{$SID}};
    ($rule) = $session->get(object => 'Infoblox::Grid::ThreatProtection::Rule', sid =>$SID);
    if (ref($rule) ne 'Infoblox::Grid::ThreatProtection::Rule') {warn "SID $SID rule not found.  Could not tweak rule settings.\n"}
    $config = $rule->config();
    if (ref($config) ne 'Infoblox::Grid::ThreatProtection::RuleConfig') {warn "SID $SID rule config not found.  Could not tweak rule settings.\n"}

    $something_changed=0;
    foreach my $param (@{$config->{params}}) {
      if (defined($rule_settings{$param->name()})) {
        $rule_tweaks{$SID}{$param->name()} = $rule_settings{$param->name()};
        if ($param->value() ne $rule_settings{$param->name()}) {
          if (! defined($changed_rules{$SID}{$param->name()})) {        # Remember the current setting for later restoration
            $changed_rules{$SID}{$param->name()} = $param->value();     # but don't overwrite the first original setting.
            if ($self->{debug}) {print "      Remembering rule $SID " . $param->name() . " original value was " . $param->value() . "\n"}
          }
          if ($self->{debug}) {print "   Changing rule $SID " . $param->name() . " from " . $param->value() . " to " . $rule_settings{$param->name()} . "\n"}
          $something_changed=1;
          $param->value($rule_settings{$param->name()});
        }
      }
    }

    $changed_rules{$SID}{DISABLED_STATE} = $rule->disable();
    if ($changed_rules{$SID}{DISABLED_STATE} eq 'true') {
      if ($self->{debug}) {print "   Enabling rule $SID\n"}
      $something_changed=1;
      $rule->disable('false');
    }

    if ($something_changed) {
      $session->modify($rule);
      if ($session->status_code()) {die "Error modifying SID $SID: " . $session->status_code() . ": " .$session->status_detail() . "\n"}
      $publish=1;
    }
  }

  if ($publish) {
    $session->publish_changes(services => 'ATP', sequential_delay => 1, member_order => 'SIMULTANEOUSLY');
    if ($session->status_code()) {die "Error publishing rule change: " . $session->status_code() . ": " .$session->status_detail() . "\n"}
    print localtime() . ": Sleeping 35 seconds for rule changes to make it to the card ...\n";
    sleep 35;
    print "Ok, here we go\n";
  }
}

################################################################################
# Restore any changed rules, back to their original settings.                  #
################################################################################
sub restore_rule_settings {
  my $self = shift;
  my ($session, $rule, $config, $something_changed);
  my $publish=0;

  if (! scalar keys %changed_rules) {return}
  $self->get_and_import_Infoblox_PAPI();

  #############################################################################################
  # Connect to the grid master, redirecting to the grid master if this is a grid member.      #
  #############################################################################################
  $session = Infoblox::Session->new('master'=>$grid_master_ip, 'username'=>'admin', 'password'=>'infoblox');
  if (ref($session) ne 'Infoblox::Session') {die "Failed to create session to $grid_master_ip\n"}
  my $return_code = $session->status_code();
  my $response = $session->status_detail();
  if ($return_code != 0) {
    if ($response =~ /This server \(.*\) is not a grid master. The current grid master is: \[?([0-9a-f\.:]*)\]?/i) {
      my $new_grid_master_ip=$1;
      my $master_addressing_mode;
      if ($new_grid_master_ip =~ /^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/) {
        $master_addressing_mode='4';
      } elsif ($new_grid_master_ip =~ /^[a-fA-f0-9]{1,4}:[a-fA-f0-9:]*$/) {
        $master_addressing_mode='6';
      }
      $grid_master_ip=$new_grid_master_ip;                  # Silently follow the redirect
      $session = Infoblox::Session->new('master'=>$grid_master_ip, 'username'=>'admin', 'password'=>'infoblox');
      $return_code = $session->status_code();
      $response = $session->status_detail();
    } else {die "Failed to connect to the $grid_master_ip grid master.  return_code=$return_code and response=$response.\n"}
  }
  if (ref($session) ne 'Infoblox::Session') {die "$myname failed to get Infoblox::Session.\n"}

  foreach my $SID (keys %changed_rules) {
    $something_changed=0;
    ($rule) = $session->get(object => 'Infoblox::Grid::ThreatProtection::Rule', sid =>$SID);
    if (ref($rule) ne 'Infoblox::Grid::ThreatProtection::Rule') {die "SID $SID rule not found\n"}
    $config = $rule->config();
    if (ref($config) ne 'Infoblox::Grid::ThreatProtection::RuleConfig') {die "SID $SID rule config not found\n"}

    if ($rule->disable() ne $changed_rules{$SID}{DISABLED_STATE}) {
      if ($self->{debug}) {print "   Restoring rule $SID back to Disabled state.\n"}
      $something_changed=1;
      $rule->disable('true');
    }

    foreach my $param (@{$config->{params}}) {
      if (defined($changed_rules{$SID}{$param->name()}) &&
               $param->value() ne $changed_rules{$SID}{$param->name()}) {
        if ($self->{debug}) {print "   Restoring rule $SID " . $param->name() . " back to " . $changed_rules{$SID}{$param->name()} . "\n"}
        $something_changed=1;
        $param->value($changed_rules{$SID}{$param->name()});
      }
    }

    if ($something_changed) {
      $publish=1;
      $session->modify($rule);
      if ($session->status_code()) {die "Error modifying SID $SID: " . $session->status_code() . ": " .$session->status_detail() . "\n"}
    }
  }

  if ($publish) {
    $session->publish_changes(services => 'ATP', sequential_delay => 1, member_order => 'SIMULTANEOUSLY');
    if ($session->status_code()) {die "Error restoring rules: " . $session->status_code() . ": " .$session->status_detail() . "\n"}
    print "\n";
    print localtime() . ": Sleeping 35 seconds for rules to get restored back to their original settings ...\n";
    sleep 35;
    print "\n";
  }
}

################################################################################
# Download the Infoblox Perl API if needed, and import it so we can use it.    #
################################################################################
sub get_and_import_Infoblox_PAPI {
  my $self = shift;
  if ($Have_Not_Imported_Infoblox_PAPI_yet) {
    if (! eval "require Infoblox") {
      if ($self->{debug}) {print "Timeout while I download the Infoblox PAPI from $grid_master_ip ...\n"}
      `mkdir /tmp/$myname.$$.PAPI`;
      system("getPAPI $grid_master_ip /tmp/$myname.$$.PAPI");
      unshift(@INC, "/tmp/$myname.$$.PAPI");
      {eval "require Infoblox";die if $@;}
    }
    Infoblox->import();
    $Have_Not_Imported_Infoblox_PAPI_yet=0;
  }
}

sub execute_test_cases {
  my $self = shift;
  my ($capture, $connected, $session, $grid_member, $start_time, $elapsed_time);

  ###############################################################################################
  # Compare each test case with the loaded rules so we know which test cases to skip, and       #
  # what kind of syslog lines to look for when we evaluate the test cases.                      #
  ###############################################################################################
  $self->review_rules_and_test_cases();

  if ($self->{need_tcpdump}) {
    # I had to manually install these Perl modules to parse through a pcap file,
    # so only load these if we need to to avoid bombing out on other's systems.
    for my $perl_module ('Net::Pcap', 'NetPacket::Ethernet qw(:strip)', 'NetPacket::IP qw(:ALL)', 'NetPacket::UDP', 'NetPacket::TCP', 'Net::DNS', 'Net::DNS::Packet') {
      if (! eval "require $perl_module") {
        die "To use traffic capture, you need the following Perl modules: Net::Pcap, NetPacket::Ethernet, NetPacket::IP, NetPacket::UDP, NetPacket::TCP, Net::DNS, Net::DNS::Packet\n";
      }
      $perl_module->import();
    }
    $self->get_and_import_Infoblox_PAPI();

    #############################################################################################
    #  In order to get the grid_member object via the PAPI, go learn what the unit's hostname   #
    #  is.  Then connect to the grid master, which is not necessarily the same IP address as    #
    #  what I'm testing, and start tcpdump.                                                     #
    #############################################################################################
    $self->{hostname}=`ssh $SSH_FLAGS root\@$self->{ssh_ip} hostname 2>/dev/null`;
    chomp $self->{hostname};
    if ($self->{debug}) {print "  Hostname is $self->{hostname}\n"}

    $connected=0;
    $start_time=time();           # Wait up to 1 minute for the grid master to respond.
    $elapsed_time=0;
    while (! $connected && $elapsed_time < 60) {
      $session = Infoblox::Session->new(master=>$self->{ssh_ip}, username=>'admin', password=>'infoblox');
      my $return_code = $session->status_code();
      my $response = $session->status_detail();

      $elapsed_time=time() - $start_time;
      if ($return_code == 0) {$connected=1}
      else {
        if ($response =~ /The version of perl module .* doesn't match the server version/) {die "$response\n"}
        if ($elapsed_time < 60) {
          print "$myname still unable to connect to $self->{ssh_ip} grid master.  Waiting 2 more seconds ...\n";
          sleep 2;
        } else {die "Giving up connecting to your $self->{ssh_ip} Grid Master with https.\n"}
      }
    }

    ($grid_member) = $session->get(object => "Infoblox::Grid::Member", name => $self->{hostname});
    if (ref($grid_member) ne 'Infoblox::Grid::Member') {die "$myname failed to get Infoblox::Grid::Member object.\n"}

    if ($self->{debug}) {print "  I'm connected to the $self->{hostname} grid master at $self->{ssh_ip} ...\n"}

    #############################################################################################
    #  Start the traffic capture on the correct interface.  See                                 #
    #      perldoc Infoblox/Grid/Member/Capture/Control                                         #
    #  for sample code.  The interface can be 'ALL' | 'HA' | 'LAN' | 'LAN2' | 'MGMT'.           #
    #############################################################################################
    $capture = Infoblox::Grid::Member::Capture::Control->new(action=>'START', interface=>$self->{capture_interface}, seconds_to_run=>(@{$self->{test_cases}} * 10));
    if (ref($capture) ne 'Infoblox::Grid::Member::Capture::Control') {die "$myname failed to get $self->{interface}/$self->{capture_interface} Infoblox::Grid::Member::Capture::Control object.  \$capture=" . (defined($capture) ? "$capture\n" : "undefined\n")}

    $grid_member->traffic_capture($capture);
  }

  ###############################################################################################
  #  Start out by delineating both /var/log/syslog and our tcpdump with a marker indicating   #
  #  the start of our tests.  This way when we read /var/log/syslog, we can get oriented to   #
  #  the start of THIS test and not get confused if there happens to be multiple runs inside    #
  #  this /var/log/syslog file.                                                               #
  #                                                                                             #
  #  If we're tracing, also mark our tcpdump with a DNS query indicating the start of this      #
  #  test.  Be aware that the way I'm marking the tcpdump is with DNS queries, so if your       #
  #  ruleset drops or alerts these normal type A queries, then you'll get inaccurate            #
  #  PASS/FAIL results.                                                                         #
  ###############################################################################################
  `ssh $SSH_FLAGS root\@$self->{ssh_ip} "> /var/log/syslog" 2>/dev/null`;
  my $timestamp=localtime();
  $self->{Test_Start_Marker}= "Start of $myname Test Suite at $timestamp";
  do {`ssh $SSH_FLAGS root\@$self->{ssh_ip} "logger '$self->{Test_Start_Marker}'" 2>/dev/null`;} until ($? == 0);
  if ($self->{need_tcpdump}) {        # Insert a marker in our tcpdump
    `dig +short +tries=1 +time=0 \@$self->{ssh_ip} Start.$myname.$timestamp.`;
  }
  print "--------------      $self->{Test_Start_Marker}      --------------\n";

  ###############################################################################################
  #  Send our Test Cases delineated with /var/log/syslog lines.                               #
  ###############################################################################################
  for (my $test_case_index=0; $test_case_index<$self->{Total_Test_Cases}; $test_case_index++) {
    my $test_case_number=$test_case_index+1;
    $timestamp = localtime();
    if ($self->{test_cases}[$test_case_index]{Status} eq 'SKIP') {
      print "$timestamp Skipping Test Case $test_case_number as promised due to $self->{test_cases}[$test_case_index]{Reason}\n";
      next;
    }

    if (defined($self->{test_cases}[$test_case_index]{pre_delay})) {sleep $self->{test_cases}[$test_case_index]{pre_delay}}
    my $Test_Case_Start_Marker = "Start of Test Case $test_case_number at $timestamp";
    do {`ssh $SSH_FLAGS root\@$self->{ssh_ip} "logger '$Test_Case_Start_Marker'" 2>/dev/null`;} until ($? == 0);
    if ($self->{need_tcpdump}) {        # Insert a marker in our tcpdump
      #####################################################################
      #  Rick, what if this dig triggers a rule?  Is there a better way   #
      #  to get a delineation string in the tcpdump?                      #
      #####################################################################
      `dig +short +tries=1 +time=0 \@$self->{test_ip} Start.Test_Case.$test_case_number.`;
    }

    #############################################################################################
    #  If a repeat count was given, then execute this command that many times, with a delay     #
    #  inbetween if specified.                                                                  #
    #############################################################################################
    if (defined($self->{test_cases}[$test_case_index]{repeat}) && $self->{test_cases}[$test_case_index]{repeat} > 1) {
      print "$timestamp: Sending Test Case $test_case_number of " . scalar(@{$self->{test_cases}}) . ": \"$self->{test_cases}[$test_case_index]{cmd}\" $self->{test_cases}[$test_case_index]{repeat} times with ";
      if (defined($self->{test_cases}[$test_case_index]{delay}) && $self->{test_cases}[$test_case_index]{delay} > 0) {
        print "$self->{test_cases}[$test_case_index]{delay} second delay.\n";
      } else {
        print "no delay.\n";
      }
      for my $i (1 .. $self->{test_cases}[$test_case_index]{repeat}) {
        print localtime() . ": Sending Test Case $test_case_number, Iteration # $i ...\n";
        $self->{test_cases}[$test_case_index]{Cmd_Output}.=`$self->{test_cases}[$test_case_index]{cmd} 2>&1`;
        if ($i < $self->{test_cases}[$test_case_index]{repeat} && defined($self->{test_cases}[$test_case_index]{delay}) && $self->{test_cases}[$test_case_index]{delay} > 0) {
          sleep $self->{test_cases}[$test_case_index]{delay};
        }
      }
    } else {
      print "$timestamp  Sending Test Case $test_case_number of " . scalar(@{$self->{test_cases}}) . ": $self->{test_cases}[$test_case_index]{cmd}\n";
      $self->{test_cases}[$test_case_index]{Cmd_Output}=`$self->{test_cases}[$test_case_index]{cmd} 2>&1`;
    }

    if (defined($self->{test_cases}[$test_case_index]{post_delay})) {sleep $self->{test_cases}[$test_case_index]{post_delay}}
    sleep 3;                   # The threat-protect-log lines takes a bit to get into /var/log/syslog.

    my $Test_Case_End_Marker = "End of Test Case $test_case_number at " . localtime();
    do {`ssh $SSH_FLAGS root\@$self->{ssh_ip} "logger '$Test_Case_End_Marker'" 2>/dev/null`;} until ($? == 0);
    if ($self->{need_tcpdump}) {        # Insert a marker in our tcpdump
      `dig +short +tries=1 +time=0 \@$self->{test_ip} End.Test_Case.$test_case_number.`;
    }
  }

  $self->{Test_End_Marker}= "End of $myname Test Suite at " . localtime();
  do {`ssh $SSH_FLAGS root\@$self->{ssh_ip} "logger '$self->{Test_End_Marker}'" 2>/dev/null`;} until ($? == 0);
  if ($self->{need_tcpdump}) {        # Insert a marker in our tcpdump
    `dig +short +tries=1 +time=0 \@$self->{test_ip} End.$myname.`;
  }
  print "--------------        $self->{Test_End_Marker}      --------------\n";
  sleep 2;

  if ($self->{need_tcpdump}) {
    #############################################################################################
    #  Stop the tcpdump and retrieve both /var/log/syslog and the traffic capture.            #
    #############################################################################################
    $capture->action('STOP');
    $grid_member->traffic_capture($capture);
  }

  `scp $SSH_FLAGS root\@$self->{ssh_ip}:/var/log/syslog $$.messages 2>/dev/null`;
  if ($self->{need_tcpdump}) {
    `scp $SSH_FLAGS root\@$self->{ssh_ip}:/storage/tmp/traffic.cap $$.traffic.cap 2>/dev/null`;
  }
}

sub evaluate {
  my $self = shift;
  my ($test_case_number, $test_case_index);

  ###############################################################################################
  #  Go through /var/log/syslog and see if we have our expected output, using our marker      #
  #  lines for orientation.                                                                     #
  #                                                                                             #
  #  Note that we do not print anything at this point.  All we do is set each test case's       #
  #  information so that the summarize function below can print it out.  We split up this       #
  #  evaluation and printing of the results in order to allow the user to skip this evaluation  #
  #  step for particular test cases.  If they choose, the user can add his own Perl logic       #
  #  inbetween the evaluate() and summarize() calls, to verify the skipped test case.           #
  #  If they carefully set the right REA instance variables, namely                             #
  #     $self->{test_cases}[$test_case_index]{Status}                                           #
  #  to either 'PASS' or 'FAIL', and                                                            #
  #     $self->{test_cases}[$test_case_index]{Reason}                                           #
  #  to some string (whether the test passed or failed!), then their conclusions can be         #
  #  included in the printed summary.                                                           #
  ###############################################################################################
  open(SYSLOG, "<$$.messages") || die "Couldn't open /var/log/syslog from $self->{ssh_ip}\n";
  my $line_number=0;

  ###############################################################################################
  # Skip through /var/log/syslog until we get to the start of our test.  This way we'll not   #
  # get confused with previous test runs.                                                       #
  ###############################################################################################
  while (<SYSLOG>) {
    $line_number++;
    if (/$self->{Test_Start_Marker}/) {last}
  }

  ###############################################################################################
  #  Examine the rest of our syslog, keeping counters for each alert and drop rule triggered.   #
  #  E.G. if we triggered the rule (i.e. the packet came from our IP address),                  #
  #       $self->{test_cases}[$test_case_index]{triggered_rules}{$sid}{ALERT} = <count>         #
  #  and  $self->{test_cases}[$test_case_index]{triggered_rules}{$sid}{DROP}  = <count>         #
  #                                                                                             #
  #  Especially at the start of the Olympic project, the rules file generated lots of useless   #
  #  threat-protect-log syslog lines for benign network traffic (e.g. IPv6 Network Discovery).  #
  #  Hopefully the rules will get cleaned up so that syslog remains uncluttered due to this     #
  #  network chatter, but until then, there's an option to do strict checking of the source     #
  #  IP address for threat-protect-log lines.  If REA->new(..., strict_source_IP_checking=>1)   #
  #  was specified, then don't use any threat-protect-log lines that were triggered by other    #
  #  IP addresses, when evaluating whether test cases PASS or FAIL.  Just keep counters of      #
  #  those hits in  $self->{rules_triggered_by_others}{$sid}{$their_IP_address} = <count>       #
  #  and print them at the end of our test suite.                                               #
  ###############################################################################################
  while (<SYSLOG>) {
    $line_number++;
    if (/Start of Test Case (\d*) at /) {
      $test_case_number=$1;
      $test_case_index=$test_case_number-1;
      $self->{test_cases}[$test_case_index]{syslog_Starting_Line} = $line_number;
      $self->{test_cases}[$test_case_index]{triggered_rules}={};

    } elsif (/End of Test Case (\d*) at /) {
      if ($test_case_number != $1) {die "Got lost parsing syslog.  Found end of test case $1 marker before end of test case $test_case_number\n"}

      $self->{test_cases}[$test_case_index]{syslog_Ending_Line} = $line_number;
      if (! defined($self->{test_cases}[$test_case_index]{skip_syslog_check}) || ! $self->{test_cases}[$test_case_index]{skip_syslog_check}) {
        #####################################################################################################################
        #  Time to evaluate this test case and determine whether it passed or failed.  We'll compare this test case's       #
        #         $self->{test_cases}[$test_case_index]{triggered_rules}{$sid}{ALERT}                                       #
        #  and    $self->{test_cases}[$test_case_index]{triggered_rules}{$sid}{DROP}  counters,                             #
        #  to its $self->{test_cases}[$test_case_index]{rules}{$sid}{alert_count}                                           #
        #  and    $self->{test_cases}[$test_case_index]{rules}{$sid}{drop_count}      expectations (if any).                #
        #                                                                                                                   #
        #  We'll set $self->{test_cases}[$test_case_index]{Status} to 'UNCHECKED' to either 'PASS' or 'FAIL', and           #
        #   also set $self->{test_cases}[$test_case_index]{Reason} to show the expected and actual results.                 #
        #####################################################################################################################
        if (%{$self->{test_cases}[$test_case_index]{rules}}) {                # If I'm expecting some rule hits,
          ###################################################################################################################
          # Go through each rule I'm expecting, sorted numerically by the rule's key, which is its SID.                     #
          ###################################################################################################################
          foreach my $sid (sort{$a <=> $b} keys %{$self->{test_cases}[$test_case_index]{rules}}) {
            if ($self->{debug}) {print "Checking if Test Case # $test_case_number triggered $self->{test_cases}[$test_case_index]{rules}{$sid}{alert_count} alert" .
                                        ($self->{test_cases}[$test_case_index]{rules}{$sid}{alert_count} eq '1' ? '' : 's') .
                                        " and $self->{test_cases}[$test_case_index]{rules}{$sid}{drop_count} drop" .
                                        ($self->{test_cases}[$test_case_index]{rules}{$sid}{drop_count} eq '1' ? '' : 's') . " for rule $sid.\n"}

            ###############################################################################################################
            # If I didn't get any Alerts or Drops for this SID, initialize the actual count to zero.                      #
            ###############################################################################################################
            if (! defined($self->{test_cases}[$test_case_index]{triggered_rules}{$sid}{ALERT})) {$self->{test_cases}[$test_case_index]{triggered_rules}{$sid}{ALERT}=0}
            if (! defined($self->{test_cases}[$test_case_index]{triggered_rules}{$sid}{DROP})) {$self->{test_cases}[$test_case_index]{triggered_rules}{$sid}{DROP}=0}

            ###############################################################################################################
            # The reason is the same whether the test case passes or fails.  If there are multiple rules to check on,     #
            # the reasons get appended with new lines.                                                                    #
            ###############################################################################################################
            if ($self->{test_cases}[$test_case_index]{Reason} ne '') {
                 if ($test_case_number < 10 ) {$self->{test_cases}[$test_case_index]{Reason}.="\n                   - "}
              elsif ($test_case_number < 100) {$self->{test_cases}[$test_case_index]{Reason}.="\n                    - "}
                                         else {$self->{test_cases}[$test_case_index]{Reason}.="\n                     - "}
            }
            $self->{test_cases}[$test_case_index]{Reason} .= "Rule $sid - Expected $self->{test_cases}[$test_case_index]{rules}{$sid}{alert_count} alert" .
                                                             ($self->{test_cases}[$test_case_index]{rules}{$sid}{alert_count} eq '1' ? '' : 's') .
                                                             " and $self->{test_cases}[$test_case_index]{rules}{$sid}{drop_count} drop" .
                                                             ($self->{test_cases}[$test_case_index]{rules}{$sid}{drop_count} eq '1' ? '' : 's') .
                                                             ".  Got $self->{test_cases}[$test_case_index]{triggered_rules}{$sid}{ALERT} alert" .
                                                             ($self->{test_cases}[$test_case_index]{triggered_rules}{$sid}{ALERT} eq '1' ? '' : 's') .
                                                             " and $self->{test_cases}[$test_case_index]{triggered_rules}{$sid}{DROP} drop" .
                                                             ($self->{test_cases}[$test_case_index]{triggered_rules}{$sid}{DROP} eq '1' ? '' : 's') . '.';

            ###############################################################################################################
            # Check Expected Alert counts with Actual for this SID.                                                       #
            ###############################################################################################################
            if ($self->{test_cases}[$test_case_index]{rules}{$sid}{alert_count} =~ /^(\d+)-(\d+)$/) {   # Expecting a range of this SID alerts?
              if ($self->{test_cases}[$test_case_index]{triggered_rules}{$sid}{ALERT} >= $1 &&
                  $self->{test_cases}[$test_case_index]{triggered_rules}{$sid}{ALERT} <= $2) {
                ###########################################################################################################
                # The actual Alert count for this SID is within range.  If this test case is unchecked, then declare      #
                # it passed so far.  It can still fail later on.                                                          #
                ###########################################################################################################
                if ($self->{test_cases}[$test_case_index]{Status} eq 'UNCHECKED') {$self->{test_cases}[$test_case_index]{Status} = 'PASS'}
              } else {
                ###########################################################################################################
                # The actual Alert count for this SID is outside the expected range.  Declare this test case failed.      #
                ###########################################################################################################
                $self->{test_cases}[$test_case_index]{Status} = 'FAIL';
                $self->{test_cases}[$test_case_index]{Reason} .= "  Ooops.";
              }
            } else {                                                                                    # Expecting an exact number of this SID alerts.
              if ($self->{test_cases}[$test_case_index]{triggered_rules}{$sid}{ALERT} == $self->{test_cases}[$test_case_index]{rules}{$sid}{alert_count}) {
                ###########################################################################################################
                # The actual Alert count for this SID is what we expected.  If this test case is unchecked, then          #
                # declare it passed so far.  It can still fail later on.                                                  #
                ###########################################################################################################
                if ($self->{test_cases}[$test_case_index]{Status} eq 'UNCHECKED') {$self->{test_cases}[$test_case_index]{Status} = 'PASS'}
              } else {
                #########################################################################################################
                # Declare this test case failed.                                                                        #
                #########################################################################################################
                $self->{test_cases}[$test_case_index]{Status} = 'FAIL';
                $self->{test_cases}[$test_case_index]{Reason} .= "  Ooops.";
              }
            }

            ###############################################################################################################
            # Check Expected Alert counts with Actual for this SID.                                                       #
            ###############################################################################################################
            if ($self->{test_cases}[$test_case_index]{rules}{$sid}{drop_count} =~ /^(\d+)-(\d+)$/) {    # Expecting a range of this SID drops?
              if ($self->{test_cases}[$test_case_index]{triggered_rules}{$sid}{DROP} >= $1 &&
                  $self->{test_cases}[$test_case_index]{triggered_rules}{$sid}{DROP} <= $2) {
                ###########################################################################################################
                # The actual Drop count for this SID is within range.  If this test case is unchecked, then declare       #
                # it passed so far.  It can still fail later on.                                                          #
                ###########################################################################################################
                if ($self->{test_cases}[$test_case_index]{Status} eq 'UNCHECKED') {$self->{test_cases}[$test_case_index]{Status} = 'PASS'}
              } else {
                ###########################################################################################################
                # The actual Drop count for this SID is outside the expected range.  Declare this test case failed.       #
                ###########################################################################################################
                $self->{test_cases}[$test_case_index]{Status} = 'FAIL';
                $self->{test_cases}[$test_case_index]{Reason} .= "  Ooops.";
              }

            } else {                                                                                    # Expecting an exact number of this SID drops.
              if ($self->{test_cases}[$test_case_index]{triggered_rules}{$sid}{DROP} == $self->{test_cases}[$test_case_index]{rules}{$sid}{drop_count}) {
                ###########################################################################################################
                # The actual Drop count for this SID is what we expected.  If this test case is unchecked, then           #
                # declare it passed so far.  It can still fail later on.                                                  #
                ###########################################################################################################
                if ($self->{test_cases}[$test_case_index]{Status} eq 'UNCHECKED') {$self->{test_cases}[$test_case_index]{Status} = 'PASS'}
              } else {
                ###########################################################################################################
                # Declare this test case failed.                                                                          #
                ###########################################################################################################
                $self->{test_cases}[$test_case_index]{Status} = 'FAIL';
                $self->{test_cases}[$test_case_index]{Reason} .= "  Ooops.";
              }
            }
          }
          #################################################################################################################
          # Now loop through all the rules that we did trigger, looking for any that we got, but weren't expecting.       #
          #################################################################################################################
          if (defined($self->{test_cases}[$test_case_index]{triggered_rules}) && scalar(%{$self->{test_cases}[$test_case_index]{triggered_rules}})) {
            foreach my $sid (sort{$a <=> $b} keys %{$self->{test_cases}[$test_case_index]{triggered_rules}}) {
              if (! defined($self->{test_cases}[$test_case_index]{rules}{$sid})) {                        # If this triggered rule is unexpected,
                ###########################################################################################################
                # If I didn't get any Alerts or Drops for this SID, initialize the actual count to zero.                  #
                ###########################################################################################################
                if (! defined($self->{test_cases}[$test_case_index]{triggered_rules}{$sid}{ALERT})) {$self->{test_cases}[$test_case_index]{triggered_rules}{$sid}{ALERT}=0}
                if (! defined($self->{test_cases}[$test_case_index]{triggered_rules}{$sid}{DROP})) {$self->{test_cases}[$test_case_index]{triggered_rules}{$sid}{DROP}=1}

                ###########################################################################################################
                # What we do with those unexpected triggered rules, is up to the test writer.  In the early days, we had  #
                # noisy rules due to extraneous (broadcast?) network traffic.  If that's all it is and the test writer    #
                # wants to ignore that noise, they can specify ignore_extra_alerts and/or ignore_extra_drops, in which    #
                # case we will mention the extra traffic, but not FAIL the test case.  If they don't specify anything,    #
                # then we will FAIL the test case.                                                                        #
                ###########################################################################################################
                if ($self->{test_cases}[$test_case_index]{Reason} ne '') {
                     if ($test_case_number < 10 ) {$self->{test_cases}[$test_case_index]{Reason}.="\n                   - "}
                  elsif ($test_case_number < 100) {$self->{test_cases}[$test_case_index]{Reason}.="\n                    - "}
                                             else {$self->{test_cases}[$test_case_index]{Reason}.="\n                     - "}
                }

                $self->{test_cases}[$test_case_index]{Reason} .= "Rule $sid - Unexpected.  Got " .
                                                                 "$self->{test_cases}[$test_case_index]{triggered_rules}{$sid}{ALERT} alert" .
                                                                 ($self->{test_cases}[$test_case_index]{triggered_rules}{$sid}{ALERT} eq '1' ? '' : 's') .
                                                                 " and $self->{test_cases}[$test_case_index]{triggered_rules}{$sid}{DROP} drop" .
                                                                 ($self->{test_cases}[$test_case_index]{triggered_rules}{$sid}{DROP} eq '1' ? '' : 's') . '.';

                if ($self->{test_cases}[$test_case_index]{triggered_rules}{$sid}{ALERT}) {
                  if (! defined($self->{test_cases}[$test_case_index]{ignore_extra_alerts}) || ! $self->{test_cases}[$test_case_index]{ignore_extra_alerts}) {
                    $self->{test_cases}[$test_case_index]{Status} = 'FAIL';
                    $self->{test_cases}[$test_case_index]{Reason} .= "  Ooops.";
                  }
                }
                if ($self->{test_cases}[$test_case_index]{triggered_rules}{$sid}{DROP}) {
                  if (! defined($self->{test_cases}[$test_case_index]{ignore_extra_drops}) || ! $self->{test_cases}[$test_case_index]{ignore_extra_drops}) {
                    $self->{test_cases}[$test_case_index]{Status} = 'FAIL';
                    $self->{test_cases}[$test_case_index]{Reason} .= "  Ooops.";
                  }
                }
              }
            }
          }
        } else {
          #################################################################################################################
          # I'm not expecting any rules to trigger with this test case.  Let's see if it got any hits.                    #
          #################################################################################################################
          if (defined($self->{test_cases}[$test_case_index]{triggered_rules}) && scalar(%{$self->{test_cases}[$test_case_index]{triggered_rules}})) {
            foreach my $sid (sort{$a <=> $b} keys %{$self->{test_cases}[$test_case_index]{triggered_rules}}) {
              #############################################################################################################
              # If I didn't get any Alerts or Drops for this SID, initialize the actual count to zero.                    #
              #############################################################################################################
              if (! defined($self->{test_cases}[$test_case_index]{triggered_rules}{$sid}{ALERT})) {$self->{test_cases}[$test_case_index]{triggered_rules}{$sid}{ALERT}=0}
              if (! defined($self->{test_cases}[$test_case_index]{triggered_rules}{$sid}{DROP})) {$self->{test_cases}[$test_case_index]{triggered_rules}{$sid}{DROP}=1}

              $self->{test_cases}[$test_case_index]{Status} = 'FAIL';
              $self->{test_cases}[$test_case_index]{Reason} .= "  Ooops.";

              if ($self->{test_cases}[$test_case_index]{Reason} ne '') {
                   if ($test_case_number < 10 ) {$self->{test_cases}[$test_case_index]{Reason}.="\n                   - "}
                elsif ($test_case_number < 100) {$self->{test_cases}[$test_case_index]{Reason}.="\n                    - "}
                                           else {$self->{test_cases}[$test_case_index]{Reason}.="\n                     - "}
              }
              $self->{test_cases}[$test_case_index]{Reason} .= "Rule $sid - Expected no alerts and no drops.  Got " .
                                                               "$self->{test_cases}[$test_case_index]{triggered_rules}{$sid}{ALERT} alert" .
                                                               ($self->{test_cases}[$test_case_index]{triggered_rules}{$sid}{ALERT} eq '1' ? '' : 's') .
                                                               " and $self->{test_cases}[$test_case_index]{triggered_rules}{$sid}{DROP} drop" .
                                                               ($self->{test_cases}[$test_case_index]{triggered_rules}{$sid}{DROP} eq '1' ? '' : 's') . '.';
            }
          } else {
            if ($self->{test_cases}[$test_case_index]{Status} eq 'UNCHECKED') {$self->{test_cases}[$test_case_index]{Status} = 'PASS'}
            $self->{test_cases}[$test_case_index]{Reason} = "Expected no alerts and no drops.  Got no alerts and no drops.";
          }
        }
      }

    } elsif (/$self->{Test_End_Marker}/) {
      $test_case_number='';
      $test_case_index='';
      last;

    } elsif (/threat-protect-log.* (?:info|emerg|err|crit) CEF:[^|]+\|[^|]+\|[^|]+\|[^|]+\|(\d+)\|.*src=([^ ]*) .* act="(\w+)" /) {
      #####################################################################################################################
      # Parse the threat-protect-log line, e.g.
      #  2013-11-08T10:30:30-08:00 daemon (none) threat-protect-log[25196]: info CEF:0|Infoblox|NIOS Threat|6.9.0-222919|5200011|DROP TCP DNS Unexpected|4|src=10.32.3.74 spt=50831 dst=10.34.9.51 dpt=53 act="DROP" cat="Default Drop"
      #####################################################################################################################
      my $triggered_sid=$1;
      my $triggered_ip=$2;
      my $triggered_type=$3;

      #####################################################################################################################
      #  If we are doing strict source IP checking and some other IP addresss triggered this rule, then just keep         #
      #  counters of the source IP address and the SID.                                                                   #
      #####################################################################################################################
      if ($self->{strict_source_IP_checking} && $triggered_ip ne $self->{my_IP_address}) {
        if ($self->{debug}) {print "Rule $triggered_sid triggered by $triggered_ip (not us) on line $line_number\n"}
        if (! defined($self->{rules_triggered_by_others})) {$self->{rules_triggered_by_others}={}}
        if (! defined($self->{rules_triggered_by_others}{$triggered_sid})) {$self->{rules_triggered_by_others}{$triggered_sid}={}}
        if (! defined($self->{rules_triggered_by_others}{$triggered_sid}{$triggered_ip})) {$self->{rules_triggered_by_others}{$triggered_sid}{$triggered_ip}=1}
                                                                                     else {$self->{rules_triggered_by_others}{$triggered_sid}{$triggered_ip}++}
      } else {
        if ($test_case_number) {                          # Are we in the middle of a test case?
          if ($self->{debug}) {print "Test Case $test_case_number triggered $triggered_type rule # $triggered_sid on line $line_number\n"}

          if (! defined($self->{test_cases}[$test_case_index]{triggered_rules}{$triggered_sid})) {
            $self->{test_cases}[$test_case_index]{triggered_rules}{$triggered_sid}={};
          }
          if (defined($self->{test_cases}[$test_case_index]{triggered_rules}{$triggered_sid}{$triggered_type})) {
            # E.G.  $self->{test_cases}[0]{triggered_rules}{5003095}{ALERT}++
            #   or  $self->{test_cases}[0]{triggered_rules}{5003095}{DROP}++
            $self->{test_cases}[$test_case_index]{triggered_rules}{$triggered_sid}{$triggered_type}++;
          } else {
            $self->{test_cases}[$test_case_index]{triggered_rules}{$triggered_sid}{$triggered_type}=1;
          }
        } else {                                          # This threat-protect-log line came outside of a test case.
          if ($self->{debug}) {print "Rule $triggered_sid triggered outside of one of our test cases on line $line_number\n"}
        }
      }
    }
  }
  close SYSLOG;

  #######################################################################
  #  Is there any command output checking wanted today?                 #
  #######################################################################
  for (my $test_case_index=0; $test_case_index<$self->{Total_Test_Cases}; $test_case_index++) {
    my $test_case_number=$test_case_index+1;

    #####################################################################
    # If this test case was skipped due to an AUTO rule condition not   #
    # being satisfied, we've already stored its Status & Reason.        #
    #####################################################################
    if ($self->{test_cases}[$test_case_index]{Status} ne 'SKIP') {
      ###################################################################
      # Was a pass_if_match specified?                                  #
      ###################################################################
      if (defined($self->{test_cases}[$test_case_index]{pass_if_match})) {
        if ($self->{test_cases}[$test_case_index]{Cmd_Output} =~ /$self->{test_cases}[$test_case_index]{pass_if_match}/s) {
          if ($self->{test_cases}[$test_case_index]{Status} eq 'FAIL') {
            if ($self->{debug}) {print "    Test case #$test_case_number matched the pass_if_match, but was already marked FAIL.\n"}
          } else {
            $self->{test_cases}[$test_case_index]{Status} = 'PASS';
          }

          if ($self->{test_cases}[$test_case_index]{Reason} ne '') {
               if ($test_case_number < 10 ) {$self->{test_cases}[$test_case_index]{Reason}.="\n                   - "}
            elsif ($test_case_number < 100) {$self->{test_cases}[$test_case_index]{Reason}.="\n                    - "}
                                       else {$self->{test_cases}[$test_case_index]{Reason}.="\n                     - "}
          }
          $self->{test_cases}[$test_case_index]{Reason} .= "Matched /$self->{test_cases}[$test_case_index]{pass_if_match}/."
        } else {
          $self->{test_cases}[$test_case_index]{Status} = 'FAIL';

          if ($self->{test_cases}[$test_case_index]{Reason} ne '') {
               if ($test_case_number < 10 ) {$self->{test_cases}[$test_case_index]{Reason}.="\n                   - "}
            elsif ($test_case_number < 100) {$self->{test_cases}[$test_case_index]{Reason}.="\n                    - "}
                                       else {$self->{test_cases}[$test_case_index]{Reason}.="\n                     - "}
          }
          $self->{test_cases}[$test_case_index]{Reason} .= "Did not match /$self->{test_cases}[$test_case_index]{pass_if_match}/.  Ooops."
        }
      }

      ###################################################################
      # Was a fail_if_match specified?                                  #
      ###################################################################
      if (defined($self->{test_cases}[$test_case_index]{fail_if_match})) {
        if ($self->{test_cases}[$test_case_index]{Cmd_Output} =~ /$self->{test_cases}[$test_case_index]{fail_if_match}/s) {
          $self->{test_cases}[$test_case_index]{Status} = 'FAIL';

          if ($self->{test_cases}[$test_case_index]{Reason} ne '') {
               if ($test_case_number < 10 ) {$self->{test_cases}[$test_case_index]{Reason}.="\n                   - "}
            elsif ($test_case_number < 100) {$self->{test_cases}[$test_case_index]{Reason}.="\n                    - "}
                                       else {$self->{test_cases}[$test_case_index]{Reason}.="\n                     - "}
          }
          $self->{test_cases}[$test_case_index]{Reason} .= "Matched /$self->{test_cases}[$test_case_index]{fail_if_match}/.  Ooops."
        } else {
          if ($self->{test_cases}[$test_case_index]{Status} eq 'FAIL') {
            if ($self->{debug}) {print "    Test case #$test_case_number matched the fail_if_match, but was already marked FAIL.\n"}
          } else {
            $self->{test_cases}[$test_case_index]{Status} = 'PASS';
          }

          if ($self->{test_cases}[$test_case_index]{Reason} ne '') {
               if ($test_case_number < 10 ) {$self->{test_cases}[$test_case_index]{Reason}.="\n                   - "}
            elsif ($test_case_number < 100) {$self->{test_cases}[$test_case_index]{Reason}.="\n                    - "}
                                       else {$self->{test_cases}[$test_case_index]{Reason}.="\n                     - "}
          }
          $self->{test_cases}[$test_case_index]{Reason} .= "Did not match /$self->{test_cases}[$test_case_index]{fail_if_match}/."
        }
      }

      ###################################################################
      # Was a pass_if_not_match specified?                              #
      ###################################################################
      if (defined($self->{test_cases}[$test_case_index]{pass_if_not_match})) {
        if ($self->{test_cases}[$test_case_index]{Cmd_Output} !~ /$self->{test_cases}[$test_case_index]{pass_if_not_match}/s) {
          if ($self->{test_cases}[$test_case_index]{Status} eq 'FAIL') {
            if ($self->{debug}) {print "    Test case #$test_case_number matched the pass_if_not_match, but was already marked FAIL.\n"}
          } else {
            $self->{test_cases}[$test_case_index]{Status} = 'PASS';
          }

          if ($self->{test_cases}[$test_case_index]{Reason} ne '') {
               if ($test_case_number < 10 ) {$self->{test_cases}[$test_case_index]{Reason}.="\n                   - "}
            elsif ($test_case_number < 100) {$self->{test_cases}[$test_case_index]{Reason}.="\n                    - "}
                                       else {$self->{test_cases}[$test_case_index]{Reason}.="\n                     - "}
          }
          $self->{test_cases}[$test_case_index]{Reason} .= "Did not match /$self->{test_cases}[$test_case_index]{pass_if_not_match}/."
        } else {
          $self->{test_cases}[$test_case_index]{Status} = 'FAIL';

          if ($self->{test_cases}[$test_case_index]{Reason} ne '') {
               if ($test_case_number < 10 ) {$self->{test_cases}[$test_case_index]{Reason}.="\n                   - "}
            elsif ($test_case_number < 100) {$self->{test_cases}[$test_case_index]{Reason}.="\n                    - "}
                                       else {$self->{test_cases}[$test_case_index]{Reason}.="\n                     - "}
          }
          $self->{test_cases}[$test_case_index]{Reason} .= "Matched /$self->{test_cases}[$test_case_index]{pass_if_not_match}/.  Ooops."
        }
      }

      ###################################################################
      # Was a fail_if_not_match specified?                              #
      ###################################################################
      if (defined($self->{test_cases}[$test_case_index]{fail_if_not_match})) {
        if ($self->{test_cases}[$test_case_index]{Cmd_Output} !~ /$self->{test_cases}[$test_case_index]{fail_if_not_match}/s) {
          $self->{test_cases}[$test_case_index]{Status} = 'FAIL';

          if ($self->{test_cases}[$test_case_index]{Reason} ne '') {
               if ($test_case_number < 10 ) {$self->{test_cases}[$test_case_index]{Reason}.="\n                   - "}
            elsif ($test_case_number < 100) {$self->{test_cases}[$test_case_index]{Reason}.="\n                    - "}
                                       else {$self->{test_cases}[$test_case_index]{Reason}.="\n                     - "}
          }
          $self->{test_cases}[$test_case_index]{Reason} .= "Did not match /$self->{test_cases}[$test_case_index]{fail_if_not_match}/.  Ooops."
        } else {
          if ($self->{test_cases}[$test_case_index]{Status} eq 'FAIL') {
            if ($self->{debug}) {print "    Test case #$test_case_number matched the fail_if_not_match, but was already marked FAIL.\n"}
          } else {
            $self->{test_cases}[$test_case_index]{Status} = 'PASS';
          }

          if ($self->{test_cases}[$test_case_index]{Reason} ne '') {
               if ($test_case_number < 10 ) {$self->{test_cases}[$test_case_index]{Reason}.="\n                   - "}
            elsif ($test_case_number < 100) {$self->{test_cases}[$test_case_index]{Reason}.="\n                    - "}
                                       else {$self->{test_cases}[$test_case_index]{Reason}.="\n                     - "}
          }
          $self->{test_cases}[$test_case_index]{Reason} .= "Matched /$self->{test_cases}[$test_case_index]{fail_if_not_match}/."
        }
      }
    }
  }

  #######################################################################
  #  Read through the traffic capture file with the Net::Pcap Perl      #
  #  package.  See ~rjasper/process.pcap.file for a start on this.      #
  #######################################################################
# TODO  ...

}


sub summarize {
  my $self = shift;
  my ($test_case_number, $fn, $Passed, $Failed, $Skipped, $Unchecked, $Unknown);
  $Passed=$Failed=$Skipped=$Unchecked=$Unknown=0;

  if ($self->{debug}) {print "\n\nPrinting summary for the $self->{Total_Test_Cases} test cases ...\n\n"}
  for (my $test_case_index=0; $test_case_index<$self->{Total_Test_Cases}; $test_case_index++) {
    $test_case_number=$test_case_index+1;
    $fn="$myname.$$.Test_Case_${test_case_number}.details";

    if ($self->{debug}) {print "    Test case #$test_case_number Status=$self->{test_cases}[$test_case_index]{Status}  counters=$Passed/$Failed/$Skipped/$Unchecked/$Unknown\n"}
    if ($self->{test_cases}[$test_case_index]{Status} eq 'PASS') {
      $Passed++;
      print "$self->{test_cases}[$test_case_index]{Status} Test Case # $test_case_number - $self->{test_cases}[$test_case_index]{Reason}\n";

    } elsif ($self->{test_cases}[$test_case_index]{Status} eq 'FAIL') {
      $Failed++;
      print "$self->{test_cases}[$test_case_index]{Status} Test Case # $test_case_number - $self->{test_cases}[$test_case_index]{Reason}  See $fn\n";
      $self->write_test_case_details($test_case_number, $fn);

    } elsif ($self->{test_cases}[$test_case_index]{Status} eq 'SKIP') {
      $Skipped++;
      print "$self->{test_cases}[$test_case_index]{Status} Test Case # $test_case_number - $self->{test_cases}[$test_case_index]{Reason}\n";

    } elsif ($self->{test_cases}[$test_case_index]{Status} eq 'UNCHECKED') {
      $Unchecked++;
      print "$self->{test_cases}[$test_case_index]{Status} Test Case # $test_case_number.  See $fn\n";
      $self->write_test_case_details($test_case_number, $fn);

    } else {
      $Unknown++;
      print "$self->{test_cases}[$test_case_index]{Status} Test Case # $test_case_number - ";
      if (defined($self->{test_cases}[$test_case_index]{Reason})) {print "$self->{test_cases}[$test_case_index]{Reason}"}
                                                             else {print "{test_cases}[$test_case_index]{Reason} was unset."}
      print "  See $fn\n";
      $self->write_test_case_details($test_case_number, $fn);
    }
  }

  #######################################################################
  # If we were doing strict_source_IP_checking of the syslog lines and  #
  # this test suite was indeed polluted with threat-protect-log lines   #
  # triggered by other boxes on our network, not us, then print out a   #
  # summary of that activity.  For example,                             #
  #                                                                     #
  # ================================================================    #
  # In addition, these other IP addresses triggered these rules:        #
  #     fe80::204:96ff:fe1d:1980 triggered rule 5200003 8 times         #
  #     10.36.1.83 triggered rule 5030040 955 times                     #
  # ================================================================    #
  #######################################################################
  if ($self->{strict_source_IP_checking} && defined($self->{rules_triggered_by_others})) {
    print "\n";
    print "=====================================================================================\n";
    print "In addition, other IP addresses triggered these rules (these usually can be ignored):\n";
    foreach my $sid (sort{$a <=> $b} keys %{$self->{rules_triggered_by_others}}) {
      foreach my $ip (keys %{$self->{rules_triggered_by_others}{$sid}}) {     # For each IP that triggered that rule,
        print "    $ip triggered rule $sid $self->{rules_triggered_by_others}{$sid}{$ip} times\n";
      }
    }
    print "=====================================================================================\n";
  }

  print "\n";
  my $width1=length($self->{Total_Test_Cases});
  if ($Passed == 1) {printf("    %${width1}s Test Case Passed\n", $Passed)}
               else {printf("    %${width1}s Test Cases Passed\n", $Passed)}
  if ($Failed == 1) {printf("    %${width1}s Test Case Failed\n", $Failed)}
               else {printf("    %${width1}s Test Cases Failed\n", $Failed)}
  # Don't print Skipped, Unchecked, and Unknown if zero.
     if ($Skipped > 1) {printf("    %${width1}s Test Cases Skipped\n", $Skipped)}
  elsif ($Skipped > 0) {printf("    %${width1}s Test Case Skipped\n", $Skipped)}
     if ($Unchecked > 1) {printf("    %${width1}s Test Cases with Unchecked Status\n", $Unchecked)}
  elsif ($Unchecked > 0) {printf("    %${width1}s Test Case with Unchecked Status\n", $Unchecked)}
     if ($Unknown > 1) {printf("    %${width1}s Test Cases With Unknown Status\n", $Unknown)}
  elsif ($Unknown > 0) {printf("    %${width1}s Test Case With Unknown Status\n", $Unknown)}
  print "==========================================================\n";
  if ($self->{Total_Test_Cases} > 1) {printf("    %${width1}s Total Test Cases in $myname\n", $self->{Total_Test_Cases})}
                                else {printf("    %${width1}s Total Test Case in $myname\n", $self->{Total_Test_Cases})}

  if (! $Have_Not_Imported_Infoblox_PAPI_yet) {`rm -rf /tmp/$myname.$$.PAPI`}
  unlink "$$.messages";
}


################################################################################
# When a test case fails, create a file detailing everything appropriate for   #
# a Jira bug, including                                                        #
#   - The date and time we ran, by who on which system, and to which address,  #
#   - The NIOS and Marvin card firmware version,                               #
#   - The full name of this program,                                           #
#   - The full list of SNORT rules if we loaded our own rules,                 #
#   - All changes we made to any rule settings,                                #
#   - The command used for this test case,                                     #
#   - The output of that command,                                              #
#   - The expected result, either the rule we expected to trigger or None.     #
#   - The actual result, either the rule we triggered or none.                 #
#   - The relevant syslog lines,                                               #
#   - anything else we can think of, e.g. tcpdump output.                      #
################################################################################
sub write_test_case_details {
  my $self = shift;
  my $test_case_number = shift;
  my $results_file = shift;

  my $test_case_index=$test_case_number-1;

  open(DETAIL_OUTPUT,">$results_file") || die "Could not open $results_file\n";

  print DETAIL_OUTPUT "Program = $myname run by $ENV{USER} on $my_hostname ($self->{my_IP_address}) at " . localtime() . "\n";
  print DETAIL_OUTPUT "NIOS Version = $self->{NIOS_version}\n";
  print DETAIL_OUTPUT "Card Firmware = $self->{firmware_version}\n";
  print DETAIL_OUTPUT "Lab ID = $self->{lab_id} (Hardware ID = $self->{hardware_id})\n";
  print DETAIL_OUTPUT "Test IP Address = $self->{test_ip} ($self->{interface}/$self->{capture_interface} Interface)\n";
  print DETAIL_OUTPUT "SSH IP Address = $self->{ssh_ip}\n";
  print DETAIL_OUTPUT "\n";
  if (defined($self->{rules_filename})) {
    if (("$self->{rules_filename}" =~ /^NIOS:/ || "$self->{rules_filename}" eq 'NIOS')) {
      if ($self->{rules_version}) {print DETAIL_OUTPUT "SNORT Rules were version $self->{rules_version} on NIOS at $nios_filename\n"}
                             else {print DETAIL_OUTPUT "SNORT Rules were on NIOS at $nios_filename\n"}
    } else {
      print DETAIL_OUTPUT "SNORT Rules were from $self->{rules_filename}\n";
      if (-l "$self->{rules_filename}") {
        print DETAIL_OUTPUT "   which is a link to " . readlink($self->{rules_filename}) . "\n";
      }
      print DETAIL_OUTPUT "SNORT Rules were:\n";
      foreach my $rule (@{$self->{rules}}) {print DETAIL_OUTPUT "  $rule\n"}
    }
  }
  print DETAIL_OUTPUT "-" x 100 . "\n";
  print DETAIL_OUTPUT "Test Case Number $test_case_number:  $self->{test_cases}[$test_case_index]{Reason}\n";
  my $prefix='Rule Changes:';
  foreach my $tweaked_rule_SID (sort keys %rule_tweaks) {
    my $settings;
    foreach my $rule_setting (sort keys %{$rule_tweaks{$tweaked_rule_SID}}) {
      if ($settings) {$settings.=', '}
      $settings .= "$rule_setting = $rule_tweaks{$tweaked_rule_SID}{$rule_setting}";
    }
    print DETAIL_OUTPUT "$prefix $tweaked_rule_SID: $settings\n";
    $prefix='             ';
  }
  print DETAIL_OUTPUT "Test Case Command = $self->{test_cases}[$test_case_index]{cmd}\n";
  print DETAIL_OUTPUT "Test Case Command Output:\n" . ($self->{test_cases}[$test_case_index]{Cmd_Output} ? "$self->{test_cases}[$test_case_index]{Cmd_Output}" : "None\n");
  print DETAIL_OUTPUT "-" x 100 . "\n";
  print DETAIL_OUTPUT "Relevant lines from /var/log/syslog are:\n";
  my $total_lines = $self->{test_cases}[$test_case_index]{syslog_Ending_Line} - $self->{test_cases}[$test_case_index]{syslog_Starting_Line} +1;
  print DETAIL_OUTPUT `head -$self->{test_cases}[$test_case_index]{syslog_Ending_Line} $$.messages | tail -$total_lines`;

  close DETAIL_OUTPUT;
}

################################################################################
# Print out a few lines of what we've learned.                                 #
################################################################################
sub print_header {
  my $self = shift;

  print "\n";
  print "Program = $myname run by $ENV{USER} on $my_hostname ($self->{my_IP_address}) at " . localtime() . "\n";
  print "NIOS Version = $self->{NIOS_version}\n";
  print "Card Firmware = $self->{firmware_version}\n";
  print "Lab ID = $self->{lab_id} (Hardware ID = $self->{hardware_id})\n";
  print "Test IP Address = $self->{test_ip} ($self->{interface}/$self->{capture_interface} Interface)\n";
  print "SSH IP Address = $self->{ssh_ip}\n";
  print "\n";
  if (defined($self->{rules_filename})) {
    if (("$self->{rules_filename}" =~ /^NIOS:/ || "$self->{rules_filename}" eq 'NIOS')) {
      if ($self->{rules_version}) {print "SNORT Rules were version $self->{rules_version} on NIOS at $nios_filename\n"}
                             else {print "SNORT Rules were on NIOS at $nios_filename\n"}
    } else {
      print "SNORT Rules were from $self->{rules_filename}\n";
      if (-l "$self->{rules_filename}") {
        print "   which is a link to " . readlink($self->{rules_filename}) . "\n";
      }
    }
  }
  print "-" x (88+length($myname)) . "\n";
}

1;

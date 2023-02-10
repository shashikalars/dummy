#!/usr/bin/perl -w

use strict;
use warnings;
use diagnostics;
use Infoblox;
use lib "/import/qaddi/vADP_Automation";
use REA;

my ($ssh_ip, $ip, $cmd, $str, $scenario, $file);
my (@result);
my (%command_list);

$ssh_ip = shift;
$ip = shift;

die "Usage: $0 <SSH IP> <IP>\n" unless (($ssh_ip =~ /^\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}$/) && ($ip =~ /^\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}$/));
$file = "/import/qaddi/vADP_Automation/admin_console.exp";

print "\nExecuting Auto Rule Test Automation\n\n";

my $session = Infoblox::Session->new(
     master   => "$ssh_ip",
     username => "admin",
     password => "infoblox"
 );

die "Session creation failed. Please re-check the given Grid VIP:$ssh_ip<>\n" unless (($session->{'statusdetail'}) eq "Operation succeeded");

%command_list= (
    #Scenario => {
    #           command => output_to_verify,
    #           command => output_to_verify,
    #           }
    "Disable and Validate monitor mode" => {
                "set adp monitor-mode off" => "Infoblox",
                "show adp" => "Threat Protection monitor mode:\\s*Disabled",
    },
    "Disable auto-rule" => {
                "set adp-debug auto-rule 110100100 off" => 'The auto rule ID 110100100 has changed to disabled. You must click "Publish Changes" from webui Security tab for this change to take effect.',
    },
);

execute();

my $test;
my @Test_Cases=(# EARLY DROP DNS named version attempts # SID: 110100100
                {cmd=>"dig +retries=0 \@$ip version.bind.", rule=>'', fail_if_match=>'no servers could be reached'},
);
$test = REA->new(ssh_ip=>$ssh_ip, test_ip=>$ip, rules_filename=>"NIOS", test_cases=>\@Test_Cases, strict_source_IP_checking=>1);
unless ($test) {die "$0: Could not configure test environment to $ip\n"}
$test->execute_test_cases();
$test->evaluate();
@result = $test->summarize();

%command_list= (
    "Enable auto-rule" => {
                "set adp-debug auto-rule 110100100 on" => 'The auto rule ID 110100100 has changed to using default setting. You must click "Publish Changes" from webui Security tab for this change to take effect.',
    },
);

execute();

@Test_Cases=(# EARLY DROP DNS named version attempts # SID: 110100100
                {cmd=>"dig +retries=0 \@$ip authors.bind.", rule=>110100100, pass_if_match=>'no servers could be reached'},
	     # Evaluate By Pass MGMT Works fine or not
                {cmd=>"dig +retries=0 \@$ssh_ip authors.bind.", rule=>'', fail_if_match=>'no servers could be reached'},
);
$test = REA->new(ssh_ip=>$ssh_ip, test_ip=>$ip, rules_filename=>"NIOS", test_cases=>\@Test_Cases, strict_source_IP_checking=>1);
unless ($test) {die "$0: Could not configure test environment to $ip\n"}
$test->execute_test_cases();
$test->evaluate();
$test->summarize();

###################### End of MAIN ######################

sub execute {
  foreach $scenario (sort keys %command_list) {
    print "$scenario\n";
    foreach $cmd (sort keys %{ $command_list{$scenario} }) {
        $str = "expect $file $ssh_ip '$cmd'";
        @result = `$str 2>&1 | grep -A 30 "$cmd"`;
        if (grep (/$command_list{$scenario}{$cmd}/, @result)) {
             print "\t$cmd \t::\tPASSED ...\n";
        } else {
             print "\t$cmd \t::\tFAILED ...\n";
             print "$cmd Output: @result\n";
        }
        sleep 10;
    }
  }
  publish_changes();
}

sub publish_changes {
    my $res = $session->publish_changes(
        'sequential_delay' => 1,
        'member_order'     => 'SIMULTANEOUSLY',
        'services'         => 'ALL',
    );

    unless($res) {
        die "\nPublish Changes failed\n";
    } else {
        print "Performed Publish Changes\n";
        sleep 60;
    }
}


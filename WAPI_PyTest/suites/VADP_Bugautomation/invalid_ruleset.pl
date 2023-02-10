#!/usr/bin/perl -w

use strict;
use warnings;
use diagnostics;
use Infoblox;
use lib "/import/qaddi/vADP_Automation";
use REA;

my ($ssh_ip, $ip, $cmd, $str, $scenario);
my ($Ruleset_Path, $Ruleset_CL, $Ruleset, $invalid_ruleset, $pass, $fail);
my (@result);

$ssh_ip = shift;
$ip = shift;
my $SSH_FLAGS = "-q -o BatchMode=yes -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ServerAliveInterval=15";

die "Usage: $0 <SSH IP> <IP>\n" unless (($ssh_ip =~ /^\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}$/) && ($ip =~ /^\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}$/));

print "\nExecuting Invalid Ruleset Test Automation\n\n";

my $session = Infoblox::Session->new(
     master   => "$ssh_ip",
     username => "admin",
     password => "infoblox"
 );

die "Session creation failed. Please re-check the given Grid VIP:$ssh_ip<>\n" unless (($session->{'statusdetail'}) eq "Operation succeeded");

$pass=$fail=0;

#Pickup the Valid Ruleset from Olympic ruleset release path and upload to the Grid
$Ruleset_Path="/import/release_archive/olympic-rule/OFFICIAL/";
$Ruleset_CL=`ls -tr ${Ruleset_Path} | tail -1`;
chomp $Ruleset_CL;
$Ruleset=`ls ${Ruleset_Path}/${Ruleset_CL}/ForSupport/ruleset*.bin2`;
chomp $Ruleset;
ruleset_upload ($Ruleset);

#Custom log into syslog to notify the start of test case
$str = `date +%s`;
chomp $str;
`ssh $SSH_FLAGS root\@$ssh_ip "logger 'Invalid Ruleset upload test on $str'" 2>/dev/null`;

#Invalid Ruleset upload to the Grid
$invalid_ruleset="/import/qaddi/vADP_Automation/ruleset-bad-1.bin2";
ruleset_upload ($invalid_ruleset);
sleep 60;

@result=`ssh $SSH_FLAGS root\@$ssh_ip "grep -A 2500 \"Invalid Ruleset upload test on $str\" /var/log/syslog" 2>/dev/null`;
#print "The content details: @result\n";

if (grep (/Threat Protection rule sid:100000060 is invalid/, @result)) {
    $pass++;
    print "Syslog updated with the invalid ruleset error\n";
} else {
    $fail++;
    print "Syslog doesn't update with the invalid ruleset error\n";
}

#publish_changes();

my $test;
my @Test_Cases=(
                # EARLY DROP DNS named author attempts # SID: 110100100
                {cmd=>"dig +retries=0 \@$ip authors.bind. chaos txt", rule=>110100100, fail_if_match=>'no servers could be reached'},
);
$test = REA->new(ssh_ip=>$ssh_ip, test_ip=>$ip, rules_filename=>"NIOS", test_cases=>\@Test_Cases, strict_source_IP_checking=>1);
unless ($test) {die "$0: Could not configure test environment to $ip\n"}
$test->execute_test_cases();
$test->evaluate();

summary();

###################### End of MAIN #######################
sub summary {
    print "Total  : " . ($pass+$fail) . "\n";
    print "Passed : $pass\n";
    print "Failed : $fail\n";
}

sub ruleset_upload {
    my $ruleset_file = shift;
    $session->import_data(
        type => "threat_protection_rule_update",
        path => "$ruleset_file",
    );
    
    if (($session->{'statusdetail'}) eq "Operation succeeded") {
        print "\nUploaded Ruleset File ($ruleset_file) to $ssh_ip.\nWaiting for few seconds to apply upload operation\n";
        sleep 15; #Let the rule update operation complete
	$pass++;
    } elsif ($session->{'statusdetail'} =~ /Ruleset .* already exists in the database/) {
        print "The ruleset already exists in the database.\n";
	$pass++;
    } else {
        print"----------------------------------------\n";
        print Infoblox::status_detail();
        print"\n----------------------------------------\n";
	$fail++;
        print "Got the above error\n";
	summary();
	exit 0;
    }
}

sub publish_changes {
    my $res = $session->publish_changes(
        'sequential_delay' => 1,
        'member_order'     => 'SIMULTANEOUSLY',
        'services'         => 'ALL',
    );

    unless($res) {
        print "\nPublish Changes failed\n";
	$fail++;
	summary();
        exit 0;
    } else {
        print "Performed Publish Changes\n";
	$pass++;
        sleep 60;
    }
}

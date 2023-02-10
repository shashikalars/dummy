#!/usr/bin/perl -w
# 
# Author : Madhu Kumar
#
# Description: 
# This script examine the recovery process of suricata by Kill Signals
# Monitors the interface responsiveness after Kill signals
# All these operation will be performed after enabling the DNS and TP Services

use strict;
use warnings;
use diagnostics;
use Infoblox;

my $ssh_ip = shift; 
my $flag = 0;
die "Usage: $0 <TP Member SSH IP>\n" unless ($ssh_ip =~ /^\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}$/);

# Creates Session
my $session = Infoblox::Session->new(
    master   => $ssh_ip,
    username => "admin",
    password => "infoblox"
    );
die "Session creation failed. Need the appropriate Infoblox Perl Modules.\n" unless (($session->{'statusdetail'}) eq "Operation succeeded");
print "\nExecuting Suricata Process Recovery Automation\n\n";

# Gets all the DNS Members
my @retrieved_objs = $session->get(
    object       => "Infoblox::Grid::Member::DNS",
    );
# Starts DNS Service on Members
foreach (@retrieved_objs) {
    if($_->enable_dns() eq "false") {
        $_->enable_dns("true");
	$flag = 1;
    } 
    $session->modify($_) or die("modify member DNS failed: ", $session->status_code() . ":" . $session->status_detail());
    print "DNS Service Started successfully on " . $_->name() . "\n";
}

# Gets all the TP Members
@retrieved_objs = $session->get(
    object       => "Infoblox::Grid::Member::ThreatProtection",
    );
# Starts TP service on Members
foreach (@retrieved_objs) {
    if($_->enable_service() eq "false") {
        $_->enable_service("true");
	$flag = 1;
    }
    $session->modify($_) or die("modify member TP Service failed: ", $session->status_code() . ":" . $session->status_detail());
    print "TP Service Started successfully on " . $_->grid_member() . "\n";
}

$session->restart(force_restart => "true");
sleep 45 if ($flag == 1);

# Variables declaration
my ($cmd, $str, $output, $file, $pass, $fail, $prev_pid, $curr_pid, $SSH_FLAGS);
my (@result, @signals, @non_signals);
my (%command_list);

$SSH_FLAGS="-q -o BatchMode=yes -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ServerAliveInterval=15";
@result = `addkeys $ssh_ip 2>&1`;
#print "Addkeys Output: @result\n";
@result = `ssh $SSH_FLAGS root\@$ssh_ip "ls -l /var/log/syslog" 2>&1`;
die "ssh to $ssh_ip is failed even after addkeys. Manually Retry it.\n" unless (grep (/root root.*messages/, @result));
$pass = 0;
$fail = 0;

@signals = ("SIGINT", "SIGKILL", "SIGTERM", "SIGSTOP", "SIGCONT");
@non_signals = ("pkill Suri");

foreach $cmd (@signals) {
    $prev_pid = `ssh $SSH_FLAGS root\@$ssh_ip 'pidof suricata' 2>/dev/null`;
    chomp $prev_pid;
    $str = "ssh $SSH_FLAGS root\@$ssh_ip 'kill -$cmd $prev_pid'";
print "cmd: $str\n";
    @result = `$str 2>&1`;
    sleep 60;
    $curr_pid = `ssh $SSH_FLAGS root\@$ssh_ip 'pidof suricata' 2>/dev/null`;
    if (($curr_pid =~ /^\d{1,6}$/) && ($prev_pid != $curr_pid)) {
        print "Kill with '$cmd' signal\t::\tPASSED ...\n";
        $pass++;
    } elsif (($prev_pid == $curr_pid) && ($cmd =~ /STOP|CONT/)) {
	print "Kill with '$cmd' signal\t::\tPASSED ...\n";
        $pass++;
    } else {
        print "Kill with '$cmd' signal\t::\tFAILED ...\n";
        print "Previous Pid: $prev_pid\nCurrent Pid: $curr_pid\nOutput: @result\n";
        $fail++;
    }
}

foreach $cmd (@non_signals) {
    $prev_pid = `ssh $SSH_FLAGS root\@$ssh_ip 'pidof suricata' 2>/dev/null`;
    $str = "ssh $SSH_FLAGS root\@$ssh_ip '$cmd'";
print "cmd: $str\n";
    @result = `$str 2>&1`;
    sleep 120;
    $curr_pid = `ssh $SSH_FLAGS root\@$ssh_ip 'pidof suricata' 2>/dev/null`;
    if (($curr_pid =~ /^\d{1,6}$/) && ($prev_pid != $curr_pid)) {
        print "Process Kill by '$cmd'\t::\tPASSED ...\n";
        $pass++;
    } else {
        print "Process Kill by '$cmd'\t::\tFAILED ...\n";
        print "Previous Pid: $prev_pid\nCurrent Pid: $curr_pid\nOutput: @result\n";
        $fail++;
    }
}

print "\nSummary\n";
print "="x80 . "\n";
print "Total  : " . ($pass+$fail) . "\n";
print "Passed : $pass\n";
print "Failed : $fail\n";

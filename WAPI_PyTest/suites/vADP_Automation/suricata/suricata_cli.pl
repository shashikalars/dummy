#!/usr/bin/perl -w

#This script executes VADP1 Suricata CLI commands
#And validates the ouput by 2 steps - 1. Success message, 2. Command specific output
#Results each command output either PASSED or FAILED
#Shows output if any command is FAILED in validation
#This script will also validate Negative scenarios of Suricata CLI commands

use strict;
use warnings;
use diagnostics;

my ($ssh_ip, $cmd, $str, $output, $file, $pass, $fail, $SSH_FLAGS);
my (@result);
my (%positive_command_list, %negative_command_list, %empty_command_list);

$ssh_ip = shift;
$SSH_FLAGS = "-q -o BatchMode=yes -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ServerAliveInterval=15";

#Root login Validation
die "Usage: $0 <SSH IP>\n" unless ($ssh_ip =~ /^\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}$/);
$output = `sed -i '/$ssh_ip/d' ~/.ssh/known_hosts`;
@result = `addkeys $ssh_ip 2>&1`;
print "Performed Addkeys\n";
@result = `ssh $SSH_FLAGS root\@$ssh_ip "ls -l /var/log/syslog" </dev/null 2>&1`;
die "ssh to $ssh_ip is failed even after addkeys. Manually Retry it.\n" unless (grep (/root root.*messages/, @result));
$file = "/import/qaddi/vADP_Automation/suricata.exp";
$pass = 0;
$fail = 0;

print "\nExecuting Suricata CLI Automation\n\n";
#CLI Commands with positive output validation 
%positive_command_list = (
    #command => output_to_verify
    #"help" => "commands: help;version;uptime;running-mode;capture-mode;dump-counters;thread-liveness;dump-tracking-table;reload-rules;pcap-mode;pcap-filter;monitor-mode;dump-rules;show-status;set-log-level;get-log-level;quit;count: 19",
    "help" => "commands: help;version;uptime;running-mode;capture-mode;dump-counters;register-tenant-handler;unregister-tenant-handler;register-tenant;reload-tenant;unregister-tenant;thread-liveness;dump-tracking-table;dump-nat-table;reload-rules;pcap-mode;pcap-filter;monitor-mode;dump-rules;report-tracking-table;report-memory-usage;show-status;set-log-level;get-log-level;iface-stat;iface-list;quit;count: 27", 
    "version" => "version:SW_ATP-\\d{1,3}.\\d{1,3}.\\d{1,3}-\\d{1,3}\\s*Infoblox-\\w{1,5}\\s*\\d{1,2};\\s*\\d{4}",
    "uptime" => "\\d{1,10}",
    "running-mode" => "workers",
    "capture-mode" => "NFQ",
    "dump-counters" => "worker-q0.*dns.memuse: \\d{1,9};dns.memcap_state.*flow.emerg_mode_entered.*flow.emerg_mode_over",
    "thread-liveness" => "Thread Worker-.*running. Processed \\d{1,10} packets.\\s*Restarted \\d{1,4} times;Thread Worker-Q1",
    "pcap-mode show" => "pcap-mode:o.*filter:.*",
    "monitor-mode show" => "monitor-mode:o.*",
    "show-status" => "version:SW_ATP.*Infoblox.*number-of-loaded-rules.*all-threads:OK",
    "get-log-level" => "Success",
);

#CLI Commands with negative output validation
%negative_command_list = (
    #command => error_output_to_verify
    "pcap-mode" => "Usage: pcap-mode on.off.show",
    "pcap-filter" => "Usage: pcap-filter all.drop.nondrop",
    "dump-tracking-table help" => "Error: Illegal syntax",
    "dump-tracking-table help" => "Usage: dump-tracking-table",
    "monitor-mode" => "Usage: monitor-mode on.off.show",
    "monitor-mode  show" => "Invalid command .monitor-mode  show.",
    "pcap-mode onn" => "Error: Illegal operand - onn",
    "set-log-level" => "Usage: set-log-level |none|emergency|alert|critical|error|warning|notice|info",
    "get-log-level as" => "Unknown command .get-log-level as.",
);

#CLI Commands with empty output validation
%empty_command_list = (
    #command => EMpty (or) Exceptional output to verify
    "pcap-mode on" => "",
    "pcap-mode off" => "",
    "pcap-filter all" => "",
    "pcap-filter drop" => "",
    "pcap-filter nondrop" => "",
    "dump-tracking-table" => "",
    "dump-rules" => "",
    "monitor-mode on" => "",
    "monitor-mode off" => "",
    "set-log-level info" => "",
    "quit" => "Quit command client",
);

print "Suricata CLI Command: Positive Responses Test Cases\n";
foreach $cmd (keys %positive_command_list) {
    $str = "expect $file $ssh_ip '$cmd'";
    @result = `$str 2>&1 | grep -A 20 -B 1 "Success:"`;
    if (grep (/$positive_command_list{"$cmd"}/, @result)) {
        print "\t$cmd \t::\tPASSED ...\n";
	$pass++;
    } else {
        print "\t$cmd \t::\tFAILED ...\n";
        print "$cmd Output: @result\n";
        $fail++;
    }
sleep 10;
}

print "Suricata CLI Command: Negative Responses Test Cases\n";
foreach $cmd (keys %negative_command_list) {
    $str = "expect $file $ssh_ip '$cmd'";
    @result = `$str 2>&1 | grep -A 20 -B 1 "Error:"`;
    if (grep (/$negative_command_list{"$cmd"}/, @result)) {
        print "\t$cmd \t::\tPASSED ...\n";
	$pass++;
    } else {
        print "\t$cmd \t::\tFAILED ...\n";
        print "$cmd Output: @result\n";
        $fail++;
    }
sleep 10;
}

$output = "";
print "Suricata CLI Command: Empty Responses Test Cases\n";
foreach $cmd (keys %empty_command_list) {
    $str = "expect $file $ssh_ip '$cmd'";
    if ($cmd eq "quit") {
        $output = `$str 2>&1 | grep -c "$empty_command_list{$cmd}"`;
	if ($output == 1) {
	     print "\t$cmd \t::\tPASSED ...\n";
	     $pass++;
	} else {
	     print "\t$cmd \t::\tFAILED ...\n";
             $fail++;
	}
sleep 10;
	next;
    }
    @result = `$str 2>&1 | grep -A 1 "Success:"`;
    if (grep (/\>\>\>/, @result)) {
        print "\t$cmd \t::\tPASSED ...\n";
	$pass++;
    } else {
        print "\t$cmd \t::\tFAILED ...\n";
        print "$cmd Output: @result\n";
        $fail++;
    }
sleep 10;
}

print "\nSummary\n";
print "="x80 . "\n";
print "Total  : " . ($pass+$fail) . "\n";
print "Passed : $pass\n";
print "Failed : $fail\n";

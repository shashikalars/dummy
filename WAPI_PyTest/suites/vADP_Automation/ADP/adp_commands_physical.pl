#!/usr/bin/perl -w

#This script executes VADP1 ADP/ADP-Debug CLI commands on Physical unit
#And validates the ouput by Command specific output
#Results each command output either PASSED or FAILED
#Shows output if any command is FAILED in validation
#This script will also validate Negative scenarios of ADP/ADP-Debug CLI commands
#Summarize the total cases passed and failed count

use strict;
use warnings;
use diagnostics;

my ($ssh_ip, $cmd, $str, $scenario, $file, $pass, $fail);
my (@result);
my (%command_list);

$ssh_ip = shift;

die "Usage: $0 <SSH IP>\n" unless ($ssh_ip =~ /^\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}$/);
$file = "/import/qaddi/vADP_Automation/admin_console.exp";

print "\nExecuting Physical ADP CLI Commands Automation\n\n";
#CLI Commands with positive output validation 
%command_list= (
    "Enable and Validate monitor mode" => {
		"set adp monitor-mode on" => "Infoblox",
		"show adp" => "Threat Protection monitor mode:\\s*Enabled",
    },
    "Disable and Validate monitor mode" => {
                "set adp monitor-mode off" => "Infoblox",
                "show adp" => "Threat Protection monitor mode:\\s*Disabled",
    },
    "Enable and Validate dropped-packet-capture as dropped-only" => {
		"set adp-debug dropped-packet-capture dropped-only" => "Maintenance Mode",
		"show adp-debug" => "Dropped packet capture mode:\\s*Only dropped packets",
    },
    "Enable and Validate dropped-packet-capture as all" => {
                "set adp-debug dropped-packet-capture all" => "Maintenance Mode",
                "show adp-debug" => "Dropped packet capture mode:\\s*All",
    },
    "Enable and Validate dropped-packet-capture as off" => {
                "set adp-debug dropped-packet-capture off" => "Maintenance Mode",
                "show adp-debug" => "Dropped packet capture mode:\\s*Disabled",
    },
    "Enable auto-rule" => {
                "set adp-debug auto-rule 130900300 on" => 'The auto rule ID 130900300 has changed to using default setting. You must click "Publish Changes" from webui Security tab for this change to take effect.',
    },
    "Disable auto-rule" => {
                "set adp-debug auto-rule 130900300 off" => 'The auto rule ID 130900300 has changed to disabled. You must click "Publish Changes" from webui Security tab for this change to take effect.',
    },
    "Enable unknown auto-rule (N)" => {
                "set adp-debug auto-rule 101 on" => 'The auto rule with sid 101 cannot be found.',
    },
    "Disable unknown auto-rule (N)" => {
                "set adp-debug auto-rule 102 off" => 'The auto rule with sid 102 cannot be found.',
    },
);

$pass = 0;
$fail = 0;

foreach $scenario (sort keys %command_list) {
    print "$scenario\n";
    foreach $cmd (sort keys %{ $command_list{$scenario} }) {
    	$str = "expect $file $ssh_ip '$cmd'";
    	@result = `$str 2>&1 | grep -A 30 "$cmd"`;
    	if (grep (/$command_list{$scenario}{$cmd}/, @result)) {
             print "\t$cmd \t::\tPASSED ...\n";
	     $pass++;
    	} else {
             print "\t$cmd \t::\tFAILED ...\n";
             print "$cmd Output: @result\n";
	     $fail++;
    	}
	sleep 10;
    }
}

print "\nSummary\n";
print "="x80 . "\n";
print "Total  : " . ($pass+$fail) . "\n";
print "Passed : $pass\n";
print "Failed : $fail\n";

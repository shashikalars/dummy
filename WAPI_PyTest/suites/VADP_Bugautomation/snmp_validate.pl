#!/usr/bin/perl -w

use strict;
use warnings;
use diagnostics;
use Infoblox;
use lib "/import/qaddi/vADP_Automation";
use REA;

my ($ssh_ip, $ip, $cmd, $str, $scenario);
my ($rule_ref, $snmp_log_file, $trap_msg, $pass, $fail);
my (@result,@trap_msgs);
my (%command_list);

$ssh_ip = shift;
$ip = shift;

die "Usage: $0 <SSH IP> <IP>\n" unless (($ssh_ip =~ /^\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}$/) && ($ip =~ /^\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}$/));

print "\nExecuting SNMP Test Automation\n\n";

my $session = Infoblox::Session->new(
     master   => "$ssh_ip",
     username => "admin",
     password => "infoblox"
 );

die "Session creation failed. Please re-check the given Grid VIP:$ssh_ip<>\n" unless (($session->{'statusdetail'}) eq "Operation succeeded");

my $object = $session->get(
     object => "Infoblox::Grid::Member::ThreatProtection::Rule",
     'sid' => '130000200',
 );

 unless($object) {
    die("Rule Retrieval failed");
 }

my $param1 = Infoblox::Grid::ThreatProtection::RuleParam->new(
    'name' => 'DROP_INTERVAL',
    'value' => '10',
);

my $config = Infoblox::Grid::ThreatProtection::RuleConfig->new(
    'action' => 'ALERT',
    'log_severity' => 'INFORMATIONAL',
    'params' => [$param1]
);

$object->config($config);

 my $response = $session->modify($object);

 print"Drop Interval Update on 130000200: ";
 print Infoblox::status_detail();
 print"\n";

 unless($response) {
    die("Drop Interval Modification failed\n");
 }

$snmp_log_file = "/tmp/snmptrap.log";
$pass=$fail=0;

$str = "curl -k1 -s -u admin:infoblox -H 'content-type:application/json' -w \"\nThe Response Code:%{http_code}\n\" https://$ssh_ip/wapi/v2.3/grid/b25lLmNsdXN0ZXIkMA?_return_fields=snmp_setting -d '{\"snmp_setting\":{\"queries_enable\":true,\"queries_community_string\": \"public\",\"traps_community_string\": \"public\",\"traps_enable\": true,\"trap_receivers\": [{\"address\": \"10.36.199.9\",\"comment\": \"Madhu FC23 Client\"}]}}' -X PUT";
@result = `$str 2>&1`;
print "The wapi response: @result\n";

#Disable the Alert rule 130000100 (using WAPI)
$str = "curl -k1 -s -u admin:infoblox 'https://$ssh_ip/wapi/v2.3/threatprotection:rule?rule=WARN%20about%20high%20rate%20inbound%20UDP%20DNS%20queries' | grep -oP '_ref.: .threatprotection.rule.\\K.*(?=:)'";
$rule_ref = `$str 2>&1`;
chomp $rule_ref;
#print "The TP Rule ref: $rule_ref<>\n";

$str = "curl -k1 -s -u admin:infoblox 'https://$ssh_ip/wapi/v2.3/threatprotection:rule/$rule_ref' -X PUT -d disable=true";
@result = `$str 2>&1`;
print "Rule Update response: @result\n";

#Enable the UDP Alert & Drop rule 130000200 (using WAPI)
$str = "curl -k1 -s -u admin:infoblox 'https://$ssh_ip/wapi/v2.3/threatprotection:rule?rule=WARN%20%26%20BLOCK%20high%20rate%20inbound%20UDP%20DNS%20queries' | grep -oP '_ref.: .threatprotection.rule.\\K.*(?=:)'";
$rule_ref = `$str 2>&1`;
chomp $rule_ref;
#print "The TP Rule ref: $rule_ref<>\n";

$str = "curl -k1 -s -u admin:infoblox 'https://$ssh_ip/wapi/v2.3/threatprotection:rule/$rule_ref' -X PUT -d disable=false";
@result = `$str 2>&1`;
print "Rule Update response: @result\n";

#Enable the UDP Alert & Drop rule 130000300 (using WAPI)
$str = "curl -k1 -s -u admin:infoblox 'https://$ssh_ip/wapi/v2.3/threatprotection:rule?rule=WARN%20about%20high%20rate%20inbound%20TCP%20DNS%20queries' | grep -oP '_ref.: .threatprotection.rule.\\K.*(?=:)'";
$rule_ref = `$str 2>&1`;
chomp $rule_ref;
#print "The TP Rule ref: $rule_ref<>\n";

$str = "curl -k1 -s -u admin:infoblox 'https://$ssh_ip/wapi/v2.3/threatprotection:rule/$rule_ref' -X PUT -d disable=false";
@result = `$str 2>&1`;
print "Rule Update response: @result\n";

publish_changes();

#Clear the SNMP log file contents
`>$snmp_log_file`;

my $test;
my @Test_Cases=(# EARLY DROP DNS named version attempts # SID: 110100200
                {cmd=>"dnsq -ns=$ip -qname=infoblox.com -qtype=A -repeat=1500 -wait=0.02", rule=>'130000200',alert_count=>1, drop_count=>'9'},
                {cmd=>"for i in {1..300} ; do dnsq -ns=$ip -qname=infoblox.com -qtype=A -protocol=tcp; done", rule=>'130000300',alert_count=>'15-18'},
);
$test = REA->new(ssh_ip=>$ssh_ip, test_ip=>$ip, rules_filename=>"NIOS", test_cases=>\@Test_Cases, strict_source_IP_checking=>1);
unless ($test) {die "$0: Could not configure test environment to $ip\n"}
$test->execute_test_cases();
$test->evaluate();
sleep 15;

print "\n\nValidating the SNMP Traps:\n";

@trap_msgs = ("Threat Protection Service TCP.UDP Flood Drop rate is above threshold","Threat Protection Service TCP.UDP Flood Drop rate is OK",
	      "Threat Protection Service TCP.UDP Flood Alert rate is above threshold","Threat Protection Service TCP.UDP Flood Alert rate is OK");
foreach (@trap_msgs) {
    $trap_msg=$_;
    snmp_log_validate();
}

#To include the WAPI and Rule hits PASS/FAIL Count
if ($fail == 0) {
    $pass = $pass + 6;
} else {
    $fail = $fail + 6;
}


print "\nSummary\n";
print "="x80 . "\n";
print "Total  : " . ($pass+$fail) . "\n";
print "Passed : $pass\n";
print "Failed : $fail\n";

###################### End of MAIN ######################

sub snmp_log_validate {
    @result = `tail $snmp_log_file`;
    #if (grep (/Threat Protection Service TCP.UDP Flood Drop rate is above threshold/, @result)) {
    if (grep (/$trap_msg/, @result)) {
	print "Found the trap:$trap_msg\n";
	$pass++;
    } else {
	print "Didn't match the trap: $trap_msg\n";
	$fail++;
    }
}

sub publish_changes {
    my $res = $session->publish_changes(
        'sequential_delay' => 1,
        'member_order'     => 'SIMULTANEOUSLY',
        'services'         => 'ALL',
    );

    unless($res) {
        die "\nPublish Changes failed\n";
	$fail++;
    } else {
        print "Performed Publish Changes\n";
	$pass++;
        sleep 60;
    }
}

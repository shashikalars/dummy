#!/usr/bin/perl -w
use strict;
use Infoblox;
use Data::Dumper;

my $ssh_ip = $ARGV[0];

my $session = Infoblox::Session->new(
     master   => "$ssh_ip",
     username => "admin",
     password => "infoblox"
 );

die "Session creation failed.\n" unless (($session->{'statusdetail'}) eq "Operation succeeded");
print "PAPI Session created successfully\n";

#Get Rule template Object
my $template = $session->search('object' => 'Infoblox::Grid::ThreatProtection::RuleTemplate', 'name' => 'RATE LIMITED UDP FQDN lookup');

my $param1 = Infoblox::Grid::ThreatProtection::RuleParam->new(
    'name' => 'FQDN',
    'value' => 'rudp.com',
);
my $param2 = Infoblox::Grid::ThreatProtection::RuleParam->new(
    'name' => 'EVENTS_PER_SECOND',
    'value' => '1',
);
my $param3 = Infoblox::Grid::ThreatProtection::RuleParam->new(
    'name' => 'PACKETS_PER_SECOND',
    'value' => '1',
);
my $param4 = Infoblox::Grid::ThreatProtection::RuleParam->new(
    'name' => 'DROP_INTERVAL',
    'value' => '5',
);

my $config = Infoblox::Grid::ThreatProtection::RuleConfig->new(
    'action' => 'ALERT',
    'log_severity' => 'MAJOR',
    'params' => [$param1, $param2, $param3, $param4]
);

#Construct an custom rule object
my $custom_rule = Infoblox::Grid::ThreatProtection::Rule->new(
    'template'   => $template,
    'comment'    => 'Test Custom Rule',
    'config'     => $config,
    'disable'    => 'false');

#Submit for custom rule addition
my $response = $session->add( $custom_rule ) || print "Add Rule Failed\n";

print "Add Rule: ";
print Infoblox::status_detail();


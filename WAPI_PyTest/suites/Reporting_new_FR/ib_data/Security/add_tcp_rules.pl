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
my $template = $session->search('object' => 'Infoblox::Grid::ThreatProtection::RuleTemplate', 'name' => 'BLACKLIST TCP FQDN lookup');

my @name = ("info-", "war-", "maj-", "cri-");
my @ls = ("INFORMATIONAL", "WARNING", "MAJOR", "CRITICAL");

for (my $i=0;$i<=3;$i++)
{
my $param1 = Infoblox::Grid::ThreatProtection::RuleParam->new(
    'name' => 'FQDN',
    'value' => "$name[$i]"."tcp.com",
);

my $config = Infoblox::Grid::ThreatProtection::RuleConfig->new(
    'action' => 'DROP',
    'log_severity' => $ls[$i],
    'params' => [$param1]
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
}



#!/usr/bin/perl
use strict;
use Infoblox;
my $ssh_ip = $ARGV[0];
my $path = $ARGV[1];
my $session = Infoblox::Session->new(
    master   => "$ssh_ip",
    username => "admin",
    password => "infoblox"
    );
die "Session creation failed. Please re-check the given Grid VIP:$ssh_ip<>\n" unless (($session->{'statusdetail'}) eq "Operation succeeded");
$session->import_data(
    type => "threat_protection_rule_update",
    path => $path,
);

if (($session->{'statusdetail'}) eq "Operation succeeded") {
    print "\nUploaded Ruleset File ($path) to $ssh_ip.\nWaiting for few seconds to apply upload operation\n";
    sleep 15; #Let the rule update operation complete
} elsif ($session->{'statusdetail'} =~ /Ruleset .* already exists in the database/) {
    print "The ruleset already exists in the database.\n";
} else {
    print Infoblox::status_detail();
    die "Got the above error\n";
}


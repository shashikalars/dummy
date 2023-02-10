#PROGRAM STARTS: Include all the modules that will be used
 use strict;
 use Infoblox;
  #Create a session to the Infoblox appliance
 my $session = Infoblox::Session->new(
     master   => shift,
     username => "admin",
     password => "infoblox"
 );
 unless ($session) {
    die("Construct session failed: ",
        Infoblox::status_code() . ":" . Infoblox::status_detail());
 }
 print "Session created successfully\n";

my @retrieved_objs = $session->get(
     'object'      => 'Infoblox::Grid::ThreatAnalytics::Member',
 );
my $analytics_member = @retrieved_objs[0];
$analytics_member->enable_service('true');

$session->modify($analytics_member);
print "Analytics service enabled successfully\n";

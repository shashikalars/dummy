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
         'object'      => 'Infoblox::Grid::Member::ThreatProtection',
     );

my $object = @retrieved_objs[0];

$object->enable_service('true');

$session->modify($object);
print "Threat Protection service enabled successfully\n";

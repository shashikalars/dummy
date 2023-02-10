#PROGRAM STARTS: Include all the modules that will be used
 use strict;
 use Infoblox;
 #Create a session to the Infoblox appliance
 my $session = Infoblox::Session->new(
     master   => shift,
     username => "admin",
     password => "infoblox"
 );
 if ($session->status_code()) {
    die("Construct session failed: ",
        $session->status_code() . ":" . $session->status_detail());
 }
 print "Session created successfully\n";

$session->publish_changes(
    'sequential_delay' => 1,
    'member_order'     => 'SIMULTANEOUSLY',
    'services'         => 'ALL',
 )
or die ("publish changes failed");

print "Changes Published Successfully\n";

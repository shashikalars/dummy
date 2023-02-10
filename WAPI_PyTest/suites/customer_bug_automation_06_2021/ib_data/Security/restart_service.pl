 use strict;
 use Infoblox;

my $subgrid_ip = shift;

 my $session = Infoblox::Session->new(
     master   => "$subgrid_ip",
     username => "admin",
     password => "infoblox"
 );
 unless ($session) {
    die("Construct session failed: ",
        Infoblox::status_code() . ":" . Infoblox::status_detail());
 }
 print "Session created successfully\n";

my $response = $session->restart(
   services      => ['DNS', 'DHCP'],
 );

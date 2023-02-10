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
     'object' => 'Infoblox::Grid::ThreatAnalytics',
 );

my $analityic = @retrieved_objs[0];

my $rpz_zone = $session->get(object => "Infoblox::DNS::Zone", name => "analytics.com");
print($rpz_zone);
print("#########################");
$analityic->dns_tunnel_black_list_rpz_zone($rpz_zone);

$session->modify($analityic)
     or die("Modify Analityics Property failed: ",
            $session->status_code() . ":" . $session->status_detail());
 print "Analityics Property modified successfully \n";

 use strict;
 use Infoblox;
 my $host_ip =  shift;
 my $session = Infoblox::Session->new(
     master   => $host_ip, 
     username => "admin",
     password => "infoblox"
     );
 unless($session){
         die("Constructor for session failed: ",
                Infoblox::status_code(). ":" . Infoblox::status_detail());
 }
 print "Sessiion created successfully.\n";
 my $mem_ip=shift;
 my $memberns1 = Infoblox::DNS::Member->new(
    ipv4addr => $mem_ip,
 );
 my $rpz1_zone = Infoblox::DNS::Zone->new (
    name     => "rpz.com",
    comment  => "this is a demo zone 1",
    disable  => "false",
    rpz_policy => "GIVEN",
    primary => $memberns1,
 );
 $session->add($rpz1_zone)
    or die("Add zone failed: ",
               $session->status_code(). ":" .$session->status_detail());
 print"Response policy zone added successfully.\n";


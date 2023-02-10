use strict;
use Infoblox;
my $host = $ARGV[0];
 
my $session = Infoblox::Session->new(
     master   => $host
     username => "admin",
     password => "infoblox"
 );
 unless ($session) {
    die("Construct session failed: ",
        Infoblox::status_code() . ":" . Infoblox::status_detail());
 }
 print "Session created successfully\n";

my $grid = $session->get(  object => "Infoblox::Grid"  );
 unless ($grid) {
     die("Get Grid failed: ",
         $session->status_code() . ":" . $session->status_detail());
 }
$grid->query_comm_string("public"); 
$session->modify($grid)
     or die("Modify Grid failed: ",
            $session->status_code() . ":" . $session->status_detail());
print "Grid object modified successfully \n";


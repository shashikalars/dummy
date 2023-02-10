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
         object => "Infoblox::Grid::DNS",
         name   => "Infoblox"
         );

my $grid_dns=@retrieved_objs[0];

$grid_dns->forwarders(["10.120.20.28"]);
$grid_dns->allow_recursive_query("true");
$grid_dns->recursive_query_list(["any"]);

$session->modify($grid_dns)
    or die("Modify dns member failed",
             $session->status_code() . ":" . $session->status_detail());
 print"Grid DNS member modified successfully \n";

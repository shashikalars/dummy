 use strict;
 use Infoblox;
 my $host_ip = $ARGV[0];
 my $pt_ip = $ARGV[1];
 #Create a session to the Infoblox appliance
 my $session = Infoblox::Session->new(
     master   => $host_ip,
     username => "admin",
     password => "infoblox"
 );
 unless ($session) {
        die("Construct session failed: ",
                Infoblox::status_code() . ":" . Infoblox::status_detail());
 }
 print "Session created successfully\n";

my @octs = split('\.',$pt_ip);
my $mgmt_lan = "$octs[0].36.$octs[2].$octs[3]";
my $pt_member = "ib-$octs[0]-$octs[1]-$octs[2]-$octs[3].infoblox.com";


 #Get grid member through session
 my @retrieved_objs = $session->get(
     object => "Infoblox::Grid::Member",
     name   => $pt_member
     );
 my $grid_member = $retrieved_objs[0];
 unless ($grid_member) {
     die("Get grid member object failed: ",
            $session->status_code() . ":" . $session->status_detail());
 }
 print"Get grid member successful \n";
$grid_member->node1_vpn_on_mgmt("true"); 
#Applying the changes
 $session->modify($grid_member)
    or die("Modify grid member failed",
             $session->status_code() . ":" . $session->status_detail());
 print"Grid member modified successfully \n";

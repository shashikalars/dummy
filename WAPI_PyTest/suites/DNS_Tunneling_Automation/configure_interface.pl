#!/usr/bin/perl

use strict;

print $ARGV[0] ."\n";

`sudo rm -rf Infoblox*`;
`getPAPI $ARGV[0] .` ;

sleep(10);
#require Infoblox;

#system("/import/tools/qa/bin/getPAPI $grid_master_ip $PAPI_directory >/dev/null");
unshift(@INC, ".");                        # Jump through hoops so this program can
{eval "require Infoblox";die if $@;Infoblox->import();} 

# use Infoblox qw (:hostaddress);

 my $session = Infoblox::Session->new(
                master   => "$ARGV[0]", 
                username => "admin",       
                password => "infoblox"    
 );

 unless ($session) {
        die("Construct session failed: ",
                Infoblox::status_code() . ":" . Infoblox::status_detail());
 }
 print "Session created successfully\n";

 my @retrieved_objs = $session->get(
     object => "Infoblox::Grid::Member",
#     name   => "hostname.com"
     );
 my $grid_member = $retrieved_objs[0];

 unless ($grid_member) {
     die("Get grid member object failed: ",
            $session->status_code() . ":" . $session->status_detail());
 }
 print"Get grid member successful \n";


 #$grid_member->mgmt_lan("10.36.31.22");
 #$grid_member->mgmt_gateway("10.36.0.1");
 #$grid_member->mgmt_mask("255.255.0.0");
 #$grid_member->mgmt_port("true");

 $grid_member->lan2_port("true");
 $grid_member->lan2_ipv4addr("10.34.160.34");
 $grid_member->lan2_gateway("10.34.160.1");
 $grid_member->lan2_mask("255.255.254.0");
 $grid_member->ipv4addr("10.34.148.34");
 $grid_member->mask("255.255.254.0");
 $grid_member->gateway("10.34.148.1");
 $grid_member->name("infoblox.localdomain");

$session->modify($grid_member)
    or die("Modify grid member failed",
             $session->status_code() . ":" . $session->status_detail());
 print"Grid member modified successfully \n";






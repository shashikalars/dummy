#PROGRAM STARTS: Include all the modules that will be used
 use strict;
 use Infoblox;
 #refers to Infoblox Appliance IP address
 my $host_ip   = shift;
#my $host_name = "infoblox.localdomain";
 #Creating a session to appliance.
 my $session = Infoblox::Session->new(
     master   => $host_ip,
     username => "admin",
     password => "infoblox"
     )
     or die("Constructor for session failed: ",
                Infoblox::status_code(). ":" .Infoblox::status_detail());
 print"Session created successfully.\n";

my @result = $session->get(
     object => "Infoblox::Grid::Member::DHCP",
     #name=>"infoblox.localdomain" ,
#     network => "10.0.0.0/24"	 
     )
     or die("get DHCP failed: ",
                $session->status_code(). ":" .$session->status_detail());
 print "get grid DHCP Objcet successful.\n";
 unless (scalar(@result) == 0) {
     my $griddhcp = $result[0];
     if ($griddhcp) {
         #Modifying the value of the specified objects.
         $griddhcp->pxe_lease_time(43200);
         #Applying the changes to appliance through session.
         $session->modify($griddhcp)
             or die("Modify DHCP failed: ",
                $session->status_code(). ":" .$session->status_detail());
                 print"Modified Grid DHCP Object successfully.\n";
              }
          } else {
              print "No Grid DHCP object found.";
          }

 use strict;
 use Infoblox;
 use Data::Dumper;
 #Create a session to the Infoblox appliance
 my $session = Infoblox::Session->new(
     master   => shift,
     username => "admin",
     password => "infoblox"
 );
 unless ($session) {
    warn("Construct session failed: ",
        Infoblox::status_code() . ":" . Infoblox::status_detail());
 }
# print "Session created successfully\n";
 my $object = $session->get(
     object => "Infoblox::Grid::DNS",
    # name   => "ib-10-35-0-48.infoblox.com"
 );

  unless ($object) {
       warn("get Grid DNS failed: ",
       $session->status_code() . ":" . $session->status_detail());
   }
  print "Grid DNS get  successfull\n";
  #print Dumper $object;
  ##  $object->forwarders(["10.120.20.28"]);
 $object->forwarders(["10.39.16.160"]);
  $object->allow_recursive_query("true");
  $object->recursive_query_list(["any"]);
  $object->allow_transfer(["any"]);

  #$object->use_lan_ipv6_port("false");
  #Apply the changes
  $session->modify($object)
   or warn("modify member DNS failed: ",
       $session->status_code() . ":" . $session->status_detail());

   print "DNS member object modified successfully \n";
 # print Dumper $object;
 # =cut

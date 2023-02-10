 use strict;
 use Infoblox;

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
            object =>"Infoblox::Grid::Reporting" ,
         );
 my $object = $retrieved_objs[0];

unless($object){
        die("Get Reporting Object failed: ",
        $session->status_code() . ":" . $session->status_detail());
        }
 print "Get Reporting object found successfully \n";

$object->cat_security("false");

  $session->modify($object)
             or die("Modify Grid reporting property object failed: ",
                        $session->status_code(). ":" .$session->status_detail());
 print "Modify Grid reporting property object modified successfully.\n";

use strict;
use Infoblox;
my $host = $ARGV[0];
my $time_zone = $ARGV[1];

#Enabling SNMP
my $session = Infoblox::Session->new(  master   => $host, username => "admin", password => "infoblox" );
unless ($session) {
    die("Construct session failed: ",
        $session->status_code() . ":" . $session->status_detail());
 }
 print "Session created successfully\n";

my $grid = $session->get(  object => "Infoblox::Grid"  );
   $grid->query_comm_string("public"); 
   $session->modify($grid);

#TimeZone
 my $object = $session->get( "object" => "Infoblox::Grid::TimeZone");
    $object->time_zone($time_zone);
    #$object->time_zone('(UTC) Coordinated Universal Time');
    $session->modify( $object )
    or die("Modify TimeZone failed. ",
         $session->status_code() . ":" . $session->status_detail());
     print "TimeZone Modified sucessfully.\n";


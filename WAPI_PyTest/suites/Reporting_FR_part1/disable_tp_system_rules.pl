#PROGRAM STARTS: Include all the modules that will be used
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

my @sid = ("100000050", "110100900", "140000100", "140000200", "140000400", "140000500", "140000600", "140000700", "140000800", "100200110", "100200120", "100200210", "100200220", "100200300", "130905000", "130905100", "130905200", "130905300", "130905400", "130900100","130900200","130900700","130900800","130900900","130901000","130901100","130901200","130901300","130901400","130901500","130901600","130901700","130901800","130901900","130902000","130902100","130902200","130902300","130902400","130902500","130902600","130902700","130902800","130902900","130903000","130903100","130903200","130903300","130903400","130903500");
my $sid;

foreach $sid (@sid)
{
my @retrieved_objs = $session->get(
     'object' => 'Infoblox::Grid::Member::ThreatProtection::Rule',
     'sid' => $sid
 );

my $object = $retrieved_objs[0];

$object->disable("true");

 $session->modify($object);
 unless ($object) {
           warn("Disabled failed: ",
                $session->status_code() . ":" . $session->status_detail());
      }
                print $session->status_code() . ":" . $session->status_detail();
		print($sid);
		
}
  print"Default Pass/Drop category is disabled successfully\n";

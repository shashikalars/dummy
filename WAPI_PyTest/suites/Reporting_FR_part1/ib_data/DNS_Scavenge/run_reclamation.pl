#Create an Infoblox::Session object

 #PROGRAM STARTS: Include all the modules that will be used
 use strict;
 use Infoblox;
 my $host = $ARGV[0];
 #Create a session to the Infoblox appliance
 my $session = Infoblox::Session->new(
     master   => $host,
     username => "admin",
     password => "infoblox"
 );
 if ($session->status_code()) {
    die("Construct session failed: ",
        $session->status_code() . ":" . $session->status_detail());
 }
 print "Session created successfully\n";

print $session->status_detail();

for (my $m=1;$m<=2;$m++)
{
 my @result = $session->get(
     object => "Infoblox::DNS::View",
     name   => "view$m",
);

print  $session->status_detail();
 unless( @result ){
     die("Get grid DNS failed: ",
     $session->status_code() . ":" . $session->status_detail());
 }
 print" Get grid DNS object found at least 1 matching entry \n";

my $grid_dns = $result[0];

my $res = $session->run_scavenging(
     object => $grid_dns,
     action => 'ANALYZE_RECLAIM', # ANALYZE_RECLAIM
 );

print $session->status_detail();
 unless($res) {
    die("Reclamation ANALYZE Operation ");
 }
 sleep 120;
}


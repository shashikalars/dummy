 use strict;
 use Infoblox;
 my $host = $ARGV[0];
 my $session = Infoblox::Session->new( master   => $host, username => "admin", password => "infoblox" );
 unless ($session) {
    die("Construct session failed: ",
        $session->status_code() . ":" . $session->status_detail());
 }
 print "Session created successfully\n";

 my @result_array = $session->get(object => "Infoblox::Grid::Reporting");
 my $var = Infoblox::Grid::Reporting::Site ->new('reporting_site' => 'single_site');
 my $for_obj = $result_array[0];
    $for_obj->cluster_mode('SINGLE_SITE');
    $for_obj->cluster_sites([$var]);
    $session->modify($result_array[0])
        or die("Update Grid/Member Reporting Properties has failed: ",
                $session->status_code(). ":" .$session->status_detail());
print "Grid/Member Reporting Properties updated successfully.\n";


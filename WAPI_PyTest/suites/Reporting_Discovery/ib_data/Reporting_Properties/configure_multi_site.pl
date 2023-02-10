 use strict;
 use Infoblox;
 my $host = $ARGV[0];
 my $session = Infoblox::Session->new(master   => $host,username => "admin",password => "infoblox");
 if ($session->status_code()) {
    die("Construct session failed: ",
        $session->status_code() . ":" . $session->status_detail());
 }
 print "Session created successfully\n";

print $session->status_detail();
my @result_array = $session->get( object => "Infoblox::Grid::Reporting");
my $ea_site1 = Infoblox::Grid::Reporting::Site ->new('reporting_site' => 'site1','priority' => '0');
my $ea_site2 = Infoblox::Grid::Reporting::Site ->new('reporting_site' => 'site2','priority' => '1');
my $for_obj = $result_array[0];
$for_obj->cluster_mode('MULTI_SITE');
$for_obj->cluster_sites([$ea_site2,$ea_site1]);
$session->modify($result_array[0])
        or die("Update Grid/Member Reporting Properties has failed: ",
                $session->status_code(). ":" .$session->status_detail());
print "Grid/Member Reporting Properties updated successfully.\n";


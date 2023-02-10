 use strict;
 use Infoblox;
 my $host = $ARGV[0];
 my $reporting_member_ip = $ARGV[1];
 my $site = $ARGV[2];
    $reporting_member_ip =~ s/\./-/g;
 my $reporting_member = "ib-".$reporting_member_ip.".infoblox.com";  #converting ip to member naming convention. 
 my $session = Infoblox::Session->new(master => $host, username => "admin",password => "infoblox");
 unless ($session) {
    die("Construct session failed: ",
        $session->status_code() . ":" . $session->status_detail());
 }
 print "Session created successfully\n";
 my @result_array = $session->get( object => "Infoblox::Grid::Member", name => $reporting_member );
 my $obj = $result_array[0];
    $obj->extensible_attributes({'ReportingSite' => $site});
    $session->modify($obj)
        or die("Update Member Properties has Reporting Site assignment failed",
                $session->status_code(). ":" .$session->status_detail());
    print "Grid/Member Properties updated successfully.\n";

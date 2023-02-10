 use strict;
 use Infoblox;
 my $host=$ARGV[0];
 my $domains=$ARGV[1];

 my $session = Infoblox::Session->new( master => $host, username => "admin", password => "infoblox" );
 unless ($session) {
    die("Construct session failed: ",
        $session->status_code() . ":" . $session->status_detail());
 }
 print "Session created successfully\n";

 my @result_array = $session->get(
     object => "Infoblox::Grid::Reporting",
 );
 my @domain_list = split(',',$domains);
 my $rep_obj=$result_array[0];
    $rep_obj->domains_for_dns_top_clients_per_domain([@domain_list]);
    $rep_obj->num_of_dns_top_clients_per_domain(10);
    $rep_obj->enable_dns_top_clients_per_domain('true');
    $session->modify($rep_obj)
         or die("Update Grid/Member Reporting Properties has failed: ",
                $session->status_code(). ":" .$session->status_detail());
print "DNS Top Clients Per Domain added successfully.\n";


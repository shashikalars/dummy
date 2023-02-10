 use strict;
 use Infoblox;
 my $host=$ARGV[0];
 my $enable=$ARGV[1];
 my $groups=$ARGV[2];

 my $session = Infoblox::Session->new( master => $host, username => "admin", password => "infoblox" );
 unless ($session) {
    die("Construct session failed: ",
        $session->status_code() . ":" . $session->status_detail());
 }
 print "Session created successfully\n";

 my @result_array = $session->get(
     object => "Infoblox::Grid::Reporting",
 );

 my $rep_obj=$result_array[0];
 my @group_list = split(',',$groups);
    if ( $enable eq 'true' ) 
    {
     $rep_obj->ip_block_groups([@group_list]);
     $rep_obj->enable_dns_query_per_ip_block_group('true');
    }
    else
    {
      $rep_obj->ip_block_groups(undef);
      $rep_obj->enable_dns_query_per_ip_block_group('false');
    }
    $session->modify($rep_obj)
         or die("Update Grid/Member Reporting Properties has failed: ",
                $session->status_code(). ":" .$session->status_detail());
print "DNS Top Clients Per Domain added successfully.\n";


 use strict;
 use Infoblox;
 my $host_ip = $ARGV[0];
 my $session = Infoblox::Session->new( master   => $host_ip, username => "admin", password => "infoblox" );
 my @result = $session->get( object=>"Infoblox::Grid::Member::Reporting",);
 my $member;
 foreach my $ref (@result)
 {
     my %node_info = %$ref;
     if ( $node_info{"role"} eq "SEARCH_HEAD_INDEXER" )
     {
       $member = $node_info{"name"}
     }
 }
 print $member

 use strict;
 use Infoblox;
 my $host = $ARGV[0];
 my $session = Infoblox::Session->new( master   => $host, username => "admin", password => "infoblox" );
 my @result_array = $session->get(object => "Infoblox::Grid::Reporting");
 print $result_array[0]->cluster_mode();


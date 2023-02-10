 use strict;
 use Infoblox;
#Retriving Forwarders HW ID to perform system related activity. 
 my $host_ip = $ARGV[0];
 my $forwarders_file = $ARGV[1];
 my $hw_info = $ARGV[2];
 my $session = Infoblox::Session->new( master   => $host_ip, username => "admin", password => "infoblox" );
 my @result = $session->get( object=>"Infoblox::Grid::Member::Reporting",);
 my $member;
 foreach my $ref (@result)
 {
     my %node_info = %$ref;
     if ( $node_info{"role"} eq "FORWARDER" )
     {
       $member = $node_info{"name"};
       $member =~ m/(\d+)-(\d+)-(\d+)-(\d+)/g;
       my $ip="$1.$2.$3.$4";
       my $hw = `grep $ip $hw_info | cut -d : -f 2`;
       open(NODE,"> $forwarders_file");
       print NODE $hw;
       close(NODE);

       open(NODE_IP,"> $forwarders_file.ip");
       print NODE_IP $ip;
       close(NODE_IP);

     }
 }

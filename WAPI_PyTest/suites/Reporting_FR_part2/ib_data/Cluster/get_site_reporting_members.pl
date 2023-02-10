 use strict;
 use Infoblox;
#Retriving Indexers HW ID to perform system related activity. 
 my $host_ip = $ARGV[0];
 my $indexers_file = $ARGV[1];
 my $hw_info = $ARGV[2];
 my $site = $ARGV[3];
 my $session = Infoblox::Session->new( master   => $host_ip, username => "admin", password => "infoblox" );
 my @result = $session->search( object=>"Infoblox::Grid::Member",name=>".*",   'extensible_attributes' => { 'ReportingSite' => $site });
 foreach my $i (@result) {
   my $member=$i->name();
   $member =~ m/(\d+)-(\d+)-(\d+)-(\d+)/g;
   my $ip="$1.$2.$3.$4";
   my $hw = `grep $ip $hw_info | cut -d : -f 2`;
   open(NODE,"> $indexers_file");
   print NODE $hw;
   close(NODE);

   open(NODE_IP,"> $indexers_file.ip");
   print NODE_IP $ip;
   close(NODE_IP);
 }


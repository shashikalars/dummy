 use strict;
 use Infoblox;
 my $host1_ip = $ARGV[0] ;
 my $host1_fqdn =  $ARGV[1];
 my $member1_ip = $ARGV[2] ;
 my $member1_fqdn =  $ARGV[3];
 my $member2_ip = $ARGV[4] ;
 my $member2_fqdn =  $ARGV[5];
 my $nsg =  $ARGV[6];

 my $session = Infoblox::Session->new(
     master   => $host1_ip, 
     username => "admin",
     password => "infoblox"
     );
 unless($session){
         die("Constructor for session failed: ",
                Infoblox::status_code(). ":" . Infoblox::status_detail());
 }
 print "Session created successfully.\n";

 my $memberns1 = Infoblox::DNS::Member->new(
     name     => $member1_fqdn,
     ipv4addr => $member1_ip,
     lead     => "false",
     stealth  => "false"
 );

 my $memberns2 = Infoblox::DNS::Member->new(
     name     => $member2_fqdn,
     ipv4addr => $member2_ip,
 );

 my $nsg = Infoblox::Grid::DNS::Nsgroup->new(
     name        => $nsg,
     primary     => $memberns1,
     secondaries => [$memberns2],
     );

 unless($nsg){
        die("Construct NSG object failed: ",
                Infoblox::status_code(). ":" .Infoblox::status_detail());
        }
 print "nsg nsg object created successfully.\n";

 $session->add($nsg)
     or die("Add ",
                $session->status_code(). ":" .$session->status_detail());
 
 print"NSG added successfully.\n";
}


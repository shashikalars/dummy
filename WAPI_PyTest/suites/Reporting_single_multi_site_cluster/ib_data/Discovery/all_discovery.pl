use Data::Dumper;
 use strict;
 use Infoblox;

my $session = Infoblox::Session->new(
     master   => "10.35.103.6",
     username => "admin",
     password => "infoblox"
 );
 unless ($session) {
    die("Construct session failed: ",
        Infoblox::status_code() . ":" . Infoblox::status_detail());
 }
 print "Session created successfully\n";

my $grid = $session->get(
     object => "Infoblox::Grid::Discovery::Properties",
 );
 unless ($grid) {
     die("Get Grid failed: ",
         $session->status_code() . ":" . $session->status_detail());
 }
 # Modify attribute value
 $grid->basic_polling_settings->netbios_scanning('true');
 $grid->basic_polling_settings->complete_ping_sweep('true');
 $grid->basic_polling_settings->smart_subnet_ping_sweep('true');





my $snmp = Infoblox::Grid::Discovery::SNMPCredential->new(
                                                          community_string => "public",
  							  comment => "api added",
);
my $snmp1 = Infoblox::Grid::Discovery::SNMPCredential->new(
                                                          community_string => "Public",
                                                          comment => "api added",
);
my $snmp2 = Infoblox::Grid::Discovery::SNMPCredential->new(
                                                          community_string => "monitor",
                                                          comment => "api added",
);
my $snmp3 = Infoblox::Grid::Discovery::SNMPCredential->new(
                                                          community_string => "qasnmp",
                                                          comment => "api added",
);

$grid->snmp_credentials([$snmp,$snmp1,$snmp2,$snmp3]);
my $cli1 = Infoblox::Grid::Discovery::CLICredential->new(
                                                          user => "admin",
                                                          'password' => 'Infoblox123',
                                                          'type' => 'SSH',
                                                          comment => "API cli"

);

my $cli2 = Infoblox::Grid::Discovery::CLICredential->new(
                                                          user => "admin",
                                                          'password' => 'Infoblox123',
                                                          'type' => 'TELNET',
                                                          comment => "API cli"

);

my $cli3 = Infoblox::Grid::Discovery::CLICredential->new(
                                                          user => "admin",
                                                          'password' => 'Infoblox',
                                                          'type' => 'SSH',
                                                          comment => "API cli"

);

my $cli4 = Infoblox::Grid::Discovery::CLICredential->new(
                                                          user => "admin",
                                                          'password' => 'Infoblox',
                                                          'type' => 'TELNET',
                                                          comment => "API cli"

);
my $cli5 = Infoblox::Grid::Discovery::CLICredential->new(
                                                          'password' => 'Infoblox123',
                                                          'type' => 'ENABLE_SSH',
                                                          comment => "API cli"

);

my $cli6 = Infoblox::Grid::Discovery::CLICredential->new(
                                                          'password' => 'Infoblox123',
                                                          'type' => 'ENABLE_TELNET',
                                                          comment => "API cli"

);
my $cli7 = Infoblox::Grid::Discovery::CLICredential->new(
                                                          'password' => 'Infoblox',
                                                          'type' => 'ENABLE_SSH',
                                                          comment => "API cli"

);

my $cli8 = Infoblox::Grid::Discovery::CLICredential->new(
                                                          'password' => 'Infoblox',
                                                          'type' => 'ENABLE_TELNET',
                                                          comment => "API cli"

);
$grid->cli_credentials([$cli1,$cli2,$cli3,$cli4,$cli5,$cli6,$cli7,$cli8]);



$session->modify($grid)
     or die("Modify Grid failed: ",
            $session->status_code() . ":" . $session->status_detail());
print "Grid object modified successfully \n";
print"=========================================\n";
print Infoblox::status_detail();
print"=========================================\n";


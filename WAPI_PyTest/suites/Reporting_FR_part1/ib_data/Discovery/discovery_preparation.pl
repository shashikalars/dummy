use Data::Dumper;
use strict;
use Infoblox;
my $host = $ARGV[0];
my $discovery_fqdn =  $ARGV[1];
my $session = Infoblox::Session->new(
     master   => $host,
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
 $grid->basic_polling_settings->port_scanning('true');
 $grid->basic_polling_settings->auto_arp_refresh_before_switch_port_polling('true');
 $grid->basic_polling_settings->device_profile('true');
 $grid->basic_polling_settings->snmp_collection('true');
 $grid->basic_polling_settings->switch_port_data_collection_polling('PERIODIC');
 $grid->basic_polling_settings->switch_port_data_collection_polling_interval(3600);



my $snmp = Infoblox::Grid::Discovery::SNMPCredential->new(
                                                          community_string => "public",
  							  comment => "api added",
);
my $snmp1 = Infoblox::Grid::Discovery::SNMPCredential->new(
                                                          community_string => "devsnmp",
                                                          comment => "api added",
);

$grid->snmp_credentials([$snmp,$snmp1]);
my $cli1 = Infoblox::Grid::Discovery::CLICredential->new(
                                                          user => "admin",
                                                          'password' => 'infoblox',
                                                          'type' => 'SSH',
                                                          comment => "API cli"

);

my $cli2 = Infoblox::Grid::Discovery::CLICredential->new(
                                                          user => "admin",
                                                          'password' => 'infoblox',
                                                          'type' => 'TELNET',
                                                          comment => "API cli"

);

my $cli5 = Infoblox::Grid::Discovery::CLICredential->new(
                                                          'password' => 'infoblox',
                                                          'type' => 'ENABLE_SSH',
                                                          comment => "API cli"

);

my $cli6 = Infoblox::Grid::Discovery::CLICredential->new(
                                                          'password' => 'infoblox',
                                                          'type' => 'ENABLE_TELNET',
                                                          comment => "API cli"

);
$grid->cli_credentials([$cli1,$cli2,$cli5,$cli6]);



$session->modify($grid)
     or die("Modify Grid failed: ",
            $session->status_code() . ":" . $session->status_detail());
print "Grid object modified successfully \n";



my $grid1 = $session->get(
     object => "Infoblox::Grid::Member::DiscoveryProperties",
     member   => $discovery_fqdn
 );
 unless ($grid1) {
     die("Get Grid failed: ",
         $session->status_code() . ":" . $session->status_detail());
 }
 

$grid1->network_view('discovery_view');
my $landiscovery = Infoblox::Grid::Member::Discovery::ScanInterface->new(
                                                          network_view => "discovery_view",
                                                          scan_interface_type => "LAN1",
);
$grid1->snmp_credentials([$landiscovery]);

$session->modify($grid1)
     or die("Modify Grid failed: ",
            $session->status_code() . ":" . $session->status_detail());
print "Grid object modified successfully \n";

use Infoblox;
my $grid_ip=$ARGV[0];
my $host_fqdn=$ARGV[1];
my $cisco_ise = $ARGV[2]; 
#Session
my $session = Infoblox::Session->new( master => $grid_ip,username => "admin", password => "infoblox" );
#Importing CS Certificate
my $result =  $session->import_data( type => "eap_ca_cert", path => "isemnt-15.pem" );
#ADD Cisco ISE
my $subscribe_setting = Infoblox::CiscoISE::SubscribeSetting->new(
     enabled_attributes   => ['DOMAINNAME' , 'ENDPOINT_PROFILE' , 'SECURITY_GROUP' , 'SESSION_STATE' , 'SSID' , 'USERNAME' , 'VLAN'],
 );

my $publish_setting =Infoblox::CiscoISE::PublishSetting->new( enabled_attributes   => ['IPADDRESS'] );

my $object = Infoblox::CiscoISE::Endpoint->new(
     address                   => $cisco_ise, #'10.36.141.15',
     bulk_download_certificate => 'isemnt-15.pem',
     client_certificate        => 'client.txt',
     subscribe_settings        => $subscribe_setting,
     publish_settings        => $publish_setting,
     subscribing_member        => $host_fqdn,
     version                   => 'VERSION_2_0',
 );

my $response = $session->add($object);

#ADD notification
my $endpoint = $session->get(object => 'Infoblox::CiscoISE::Endpoint', address => $cisco_ise );
#From 7.3.5 onwards we have to use following updated Perl Module. 
my $publish_setting = Infoblox::CiscoISE::PublishSetting->new( 'enabled_attributes' => [ "CLIENT_ID", "FINGERPRINT", "HOSTNAME", "INFOBLOX_MEMBER", "IPADDRESS", "LEASE_END_TIME", "LEASE_START_TIME", "LEASE_STATE", "MAC_OR_DUID", "NETBIOS_NAME"]);
print Infoblox::status_detail();
my $start_list = Infoblox::Notification::RuleExpressionOp->new( op1_type => 'LIST', op => 'AND');
my $op1 = Infoblox::Notification::RuleExpressionOp->new( op1_type => 'FIELD', op1 => 'DHCP_LEASE_STATE',  op => 'EQ',op2 => 'STARTED', op2_type => 'STRING' );
my $end_list = Infoblox::Notification::RuleExpressionOp->new( op1_type => 'LIST', op => 'ENDLIST');
my $notification_rule = Infoblox::Notification::Rule->new(
     event_type                => 'DHCP_LEASES',
     expression_list           => [$start_list,$op1,$end_list],
     name                      => 'RULE1-DHCP', 
     notification_action       => 'CISCOISE_PUBLISH',
     notification_target       => $endpoint, 
     disable                   => 'false',
     publish_settings          => $publish_setting,
     override_publish_settings => 'true',
 );
my $response = $session->add($notification_rule);
print Infoblox::status_detail();

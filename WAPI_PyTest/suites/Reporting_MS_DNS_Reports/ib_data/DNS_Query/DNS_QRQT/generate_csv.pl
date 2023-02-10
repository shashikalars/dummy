my $fqdn=$ARGV[0];
my $csv_name=$ARGV[1];
my @zones=("qrqt1.com","qrqt2.com");
open(MYOUTFILE, ">$csv_name");
my $view="default";
print MYOUTFILE "header-authzone,fqdn*,zone_format*,allow_active_dir,allow_query,allow_transfer,allow_update,allow_update_forwarding,comment,create_underscore_zones,disable_forwarding,disabled,external_primaries,external_secondaries,grid_primaries,grid_secondaries,is_multimaster,notify_delay,ns_group,prefix,_new_prefix,soa_default_ttl,soa_email,soa_expire,soa_mnames,soa_negative_ttl,soa_refresh,soa_retry,soa_serial_number,update_forwarding,view,zone_type\n";
print MYOUTFILE "header-arecord,address*,_new_address,fqdn*,_new_fqdn,comment,create_ptr,disabled,ttl,view\n";
print MYOUTFILE "header-aaaarecord,address*,_new_address,fqdn*,_new_fqdn,comment,disabled,ttl,view\n";
print MYOUTFILE "header-cnamerecord,fqdn*,_new_fqdn,canonical_name,comment,disabled,ttl,view\n";
print MYOUTFILE "header-mxrecord,fqdn*,_new_fqdn,mx*,_new_mx,priority*,_new_priority,comment,disabled,ttl,view\n";
print MYOUTFILE "header-txtrecord,fqdn*,_new_fqdn,text*,_new_text,comment,disabled,ttl,view\n";
print MYOUTFILE "header-srvrecord,fqdn*,_new_fqdn,port*,_new_port,priority*,_new_priority,target*,_new_target,weight*,_new_weight,comment,disabled,ttl,view\n";
print MYOUTFILE "header-nsrecord,dname*,_new_dname,fqdn*,view,zone_nameservers\n";
print MYOUTFILE "header-dnamerecord,fqdn*,_new_fqdn,target*,comment,disabled,ttl,view\n";
print MYOUTFILE "header-naptrrecord,fqdn*,_new_fqdn,order*,_new_order,preference*,_new_preference,replacement*,_new_replacement,comment,disabled,flags,_new_flags,regexp,_new_regexp,services,_new_services,ttl,view\n";
print MYOUTFILE "header-ptrrecord,dname*,_new_dname,address,_new_address,comment,disabled,fqdn,_new_fqdn,ttl,view\n";
print MYOUTFILE "header-hostaddress,address*,_new_address,parent*,boot_file,boot_server,broadcast_address,configure_for_dhcp,configure_for_dns,deny_bootp,domain_name,domain_name_servers,ignore_dhcp_param_request_list,lease_time,mac_address,match_option,network_view,next_server,pxe_lease_time,pxe_lease_time_enabled,routers,view\n";
print MYOUTFILE "header-hostrecord,fqdn*,_new_fqdn,addresses,aliases,comment,configure_for_dns,_new_configure_for_dns,disabled,ipv6_addresses,network_view,ttl,view\n";

foreach my $zone (@zones)
{
print MYOUTFILE "authzone,$zone,FORWARD,,,,,,,FALSE,FALSE,FALSE,,,$fqdn/False/False/False,,FALSE,,,,,,,,,,,,1,,$new_view[$view],Authoritative\n";
 for( my $j=1;$j<=240; $j++)
 {
   print MYOUTFILE "arecord,10.10.1.$j,,arec$j.$zone,,,,False,,$new_view[$view]\n";
 }
 for( my $j=1;$j<=240; $j++)
 {
   print MYOUTFILE "aaaarecord,1234::9,,aaaa$j.$zone,,,False,,$new_view[$view]\n";
 }

 for( my $j=1;$j<=180; $j++)
 {
   print MYOUTFILE "cnamerecord,cname$j.$zone,,arec1.test_2.com,,False,,$new_view[$view]\n";
 }
 for( my $j=1;$j<=180; $j++)
 {
   print MYOUTFILE "mxrecord,mx$j.$zone,,exchanger.stub_2.com,,10,,,False,,$new_view[$view]\n";
 }

 for( my $j=1;$j<=180; $j++)
 {
   print MYOUTFILE "txtrecord,txt$j.$zone,,string_2,,,False,,$new_view[$view]\n";
 }
 for( my $j=1;$j<=120; $j++)
 {
   print MYOUTFILE "srvrecord,srv$j.$zone,,1,,1,,srv1.target.test.org,,1,,,False,,$new_view[$view]\n";
 }

 for( my $j=1;$j<=120; $j++)
 {
   print MYOUTFILE "dnamerecord,dname$j.$zone,,target.$zone,,False,,$new_view[$view]\n";

 }

 for( my $j=1;$j<=120; $j++)
 {
   print MYOUTFILE "naptrrecord,naptr$j.$zone,,10,,10,,.,,,False,U,,,,http+E2U,,,$new_view[$view]\n";
 }


 for( my $j=1;$j<=60; $j++)
 {
   print MYOUTFILE "ptrrecord,forward_ptr$j.com,,,,,False,ptr$j.$zone,,,$new_view[$view]\n";
 }

 for( my $j=1;$j<=60; $j++)
 {
  print MYOUTFILE "hostrecord,host$j.$zone,,12.12.12.$j,,,True,,False,,default,,$new_view[$view]\n";
  print MYOUTFILE "hostaddress,12.12.12.$j,,host$j.$zone,,,,False,True,,,,,,,,default,,,,,$new_view[$view]\n";
 }
}
close(MYOUTFILE);

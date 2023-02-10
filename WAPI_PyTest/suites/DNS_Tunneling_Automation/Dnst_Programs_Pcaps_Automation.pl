#!/usr/bin/perl
use strict;
use warnings;
use diagnostics;
use Data::Dumper;
use Expect;
use Term::ANSIColor;
use Getopt::Std;
use Net::OpenSSH;
use XML::Simple;
use Time::Piece;
use FindBin '$Bin';
use Spreadsheet::WriteExcel;
use List::Util qw(shuffle max);
use POSIX;
my ($status,$result,$program_name,$syslog_timestamp,$current_time,$server_command,$client_command,$server_daemon,$client_process,$redirect_file,$nios_version,$hardware_type);
#my ($time_elapsed,$blacklists);
my $time_elapsed=0;
my $blacklists;
my ($i, $j, $flag, $whitelist_flag, $negative_test)=0;
my $rpz_license_flag=0;
my $threat_analytics_license_flag=0;
my $preparation=0;
my (@inputs,@blacklist_domains,@syslog_content,@dnst_programs);
my $myname="$0";
my %output_summary;
$myname=~s/\.*\///;
my ($test,$session,$ssh,$cmd_output,$output_dir);
my $sudo_prefix='';
if ($ENV{USER} ne 'root') {$sudo_prefix='sudo'}
my $PAPI_directory="/tmp/$myname.$$";
my $SSH_FLAGS="-q -o BatchMode=yes -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ServerAliveInterval=15 -o LogLevel=quiet";
my @str=("Not found");
my $val="";
my %option = ();
my $prompt = "Infoblox >.*";
my $usernamePrompt = "login: ";
my $pwPrompt = "admin@.*'s password";
my @testcaseoutput;
my $match_found=0;
my @error_log;
my @output_log;
my $move_to_whitelist_flag=0;
my $run_move_to_whitelist_test=0;
my @move_to_whitelist_cases="";
my @analytics_content="";
my @classification_confidence="";
my $analytics_timestamp;
my $path;
my $max_confidence;
my $dut_dnst_threshold;
my $dut_analytics_version;
my $rea_query_test_run=0;
my $retry=0;
getopts("i:p:w:q:", \%option);

if(defined($option{p})) { 
  $preparation=1 if($option{p} eq "YES");
  $preparation=0 if($option{p} eq "NO");
}

if(defined($option{q})) {
  $rea_query_test_run=1 if($option{q} eq "YES");
  $rea_query_test_run=0 if($option{q} eq "NO");
}

if(!defined($option{i})) {
  $option{i} = "NONE";
}

if(defined($option{w})) {
  $run_move_to_whitelist_test=1 if($option{w} eq "YES");
  $run_move_to_whitelist_test=0 if($option{w} eq "NO");
}

if($rea_query_test_run == 0  &&  $run_move_to_whitelist_test == 0 && $option{i} eq "NONE") {
  print "ERROR: At least one of the options(input files path(-i) or move to whitelist(-w) or rea dns query(-q)) should be provided \n";
  print "ERROR: The format of the commmand is\n";
  print "       $0 -i <input files path> -w <YES|NO> -q <YES|NO> -p <YES|NO>\n";
  print "       $0 -i <input files path> -w <YES|NO> -q <YES|NO> -p <YES|NO>\n";
  exit(1);
}

if($option{i} ne "NONE") {
  $path=$option{i};

#Read all the files from the given path

  opendir my $dir, "$path" or die "ERROR: Cannot open directory: $!";
  my @files = readdir $dir;
  closedir $dir;

  foreach(@files) {
    if($_  !~ m/^\./) {
      push(@inputs,"$_");
    }
  }

  if(scalar(@inputs) == 0) {
    print "\nERROR: Directory is blank ... Aborting\n";
    exit(1);
  }

  local $"="\n";
  @dnst_programs = shuffle @inputs;
  print "\nRunning below dnst programs/pcaps ....\n";
  print "@dnst_programs" . "\n\n";
}

#Input file Configuration.xml existence check, abort if the file is not present 

if(! -e "Configuration.xml") {
  print "ERROR: Configuration.xml configuration file doesn't exist\n";
  exit 1;
}

#Parse the xml input 

my $configuration_ref = XMLin("Configuration.xml",'KeyAttr' => []);

if(defined($option{w})) {
  if ($$configuration_ref{WHITELIST}{movetowhitelist} =~ m/pcap$/) {
    die "Sorry, Move to whitelist test case is not supported as yet for pcaps, only works for programs, please specify a program name\n";
  }
  if(ref($$configuration_ref{WHITELIST}{movetowhitelist}) ne "HASH") {
    @move_to_whitelist_cases=split(/\,/, $$configuration_ref{WHITELIST}{movetowhitelist});
  }
  if(scalar(@move_to_whitelist_cases)==0) {
   die "Move to whitelist dnst_program is not specified in Configuration.xml.. Aborting\n";
  }
}

#############################################################################################
## Get the Unit configuration details and input definition/declaration                      #
#############################################################################################

my ($ssh_ip,$grid_master_ip);
$grid_master_ip = $$configuration_ref{SYSTEM_CONFIG}{GRID_IP} if(ref($$configuration_ref{SYSTEM_CONFIG}{GRID_IP}) ne "HASH");
$grid_master_ip = $$configuration_ref{SYSTEM_CONFIG}{DUT_MGMT_IP} if((ref($$configuration_ref{SYSTEM_CONFIG}{GRID_IP}) eq "HASH") && (ref($$configuration_ref{SYSTEM_CONFIG}{DUT_MGMT_IP}) ne "HASH"));
$grid_master_ip = $$configuration_ref{SYSTEM_CONFIG}{DUT_LAN1_IP} if((ref($$configuration_ref{SYSTEM_CONFIG}{GRID_IP}) eq "HASH") && (ref($$configuration_ref{SYSTEM_CONFIG}{DUT_MGMT_IP}) eq "HASH"));
#$ssh_ip = $$configuration_ref{SYSTEM_CONFIG}{DUT_LAN1_IP};
$ssh_ip = $$configuration_ref{SYSTEM_CONFIG}{DUT_MGMT_IP};

my $zone_name;
$zone_name= $$configuration_ref{SYSTEM_CONFIG}{RPZ_ZONE} if(ref($$configuration_ref{SYSTEM_CONFIG}{RPZ_ZONE}) ne "HASH");
$zone_name="rpz_local" if(ref($$configuration_ref{SYSTEM_CONFIG}{RPZ_ZONE}) eq "HASH");

##############################################################################################
## Get the Perl API                                                                          #
##############################################################################################
system("/import/tools/qa/bin/getPAPI $grid_master_ip $PAPI_directory >/dev/null");
unshift(@INC, "$PAPI_directory");                        # Jump through hoops so this program can
{eval "require Infoblox";die if $@;Infoblox->import();}  # use the just-now uploaded Perl API.

create_session();

#initial setup
initial_preparation() if($preparation);
addkeys() if(!$preparation);

#Get DUT environment details

test_env_details();
$current_time=`ssh root\@$ssh_ip $SSH_FLAGS date +%FT%T`;
print "\nTest start time: $current_time\n";
my $test_start_time=$current_time;
my $start=time();
 
#Create test output directory

my $timestamp=`date +%H%M`;
chomp($timestamp);
$output_dir= "output_v" . $nios_version . "_" . $timestamp;
`mkdir $output_dir`;

$myname=~s/\..*//;

#Set dnst tunneling detection threshold

set_dnst_detection_threshold() if($$configuration_ref{SYSTEM_CONFIG}{DNST_DETECTION_THRESHOLD} ne "default");
sleep(5);

#Fetch DUT analytics version

$dut_analytics_version=`ssh root\@$ssh_ip $SSH_FLAGS zgrep DnstConf /infoblox/var/analytics/logs/* | egrep -i 'DnstConf.*?version=\\d*' | grep -v unknown | head -1 | cut -d'=' -f2 2>/dev/null`;
chomp($dut_analytics_version);

print "INFO: Analytics engine version is : $dut_analytics_version \n";

#Fetch DUT Threshold values

$dut_dnst_threshold=`ssh root\@$ssh_ip $SSH_FLAGS zgrep DnstConf /infoblox/var/analytics/logs/* | egrep -i 'DnstConf.*?detection.threshold=\\d*' | tail -1 | cut -d'=' -f2 2>/dev/null`;
chomp($dut_dnst_threshold);

print "INFO: Analytics dnst threshold value is : $dut_dnst_threshold \n";
print "\n\n";

#Get whitelist_ programs/pcaps details

my @whitelists=split(/\,/, $$configuration_ref{WHITELIST}{whitelist});
my @whitelist_domains=split(/\,/,$$configuration_ref{WHITELIST}{whitelistdomains});
if(scalar(@whitelist_domains)>=1 && ref($$configuration_ref{WHITELIST}{whitelistdomains}) ne "HASH") {
  add_whitelist_domains(@whitelist_domains);
  print "\n\n\n";
}

my @negative_tests=split(/\,/, $$configuration_ref{NEGATIVE_TESTS}{testcases});

#Initiate the test suite execution

run_test() if($option{i} ne "NONE");

#Move to whitelist test

move_to_whitelist() if($run_move_to_whitelist_test);

#TCP Test cases

Rea_Dnst_query_test() if ($rea_query_test_run);

#Cleanup added whitelist domains

if(scalar(@whitelist_domains)>=1 && ref($$configuration_ref{WHITELIST}{whitelistdomains}) ne "HASH") {
  remove_whitelist_domains(@whitelist_domains);
}

restart_services();

#Print the summary report and generate xls report file

print_summary();

#Generate Junit report xml for Jenkins reporting
generate_junit_report();


##############################################################################################
## Core Module to initiate the test sequence                                                 #
##############################################################################################

sub run_test
{
  $match_found=0;
  my $array_index=0;
  foreach (@dnst_programs)
  {
    $retry=0;
    my $testcase_start_time=time();
    @error_log="";
    @output_log="";
    my $forwarder;
    $program_name="$_";
    if($program_name ~~ @whitelists) { 
      $whitelist_flag=1;
    } else {
      $whitelist_flag=0;
    }
    if($program_name ~~ @negative_tests) {
      $negative_test=1;
    } else {
      $negative_test=0;
    }
    $status="successful";
    $redirect_file="$output_dir/$_.log";
    print "INFO: Running the program \'$_\' \n" if($_ !~ m/pcap$/);
    push(@output_log,"INFO: Running the program \'$_\'") if($_ !~ m/pcap$/);

#Redirect the execution details into a file  

    open(FH,"> $redirect_file") or die "Could not write the test case details file.\n";

    if ($_ =~ m/pcap$/) {
      print "INFO: Replaying the pcap file  $_ \n";
      push(@output_log,"INFO: Replaying the pcap file \'$_\'");

#Copy the pcap files to the server and client 

      pcap_file_copy($$configuration_ref{SYSTEM_CONFIG}{TUNS_MGMT_IP},$program_name);
      pcap_file_copy($$configuration_ref{SYSTEM_CONFIG}{TUNC_MGMT_IP},$program_name);

#Update global forwarder with pcap listening/tunserver IP and additional IT DNS resolver 

      $forwarder=[$$configuration_ref{FORWARDERS}{PCAP_LISTENING_IP},"10.102.3.10"];
      #$forwarder=[$$configuration_ref{FORWARDERS}{PCAP_LISTENING_IP}];

#Update forwarders only when this condition is not true the previous array element is pcap 

      if($array_index==0) {
        update_forwarder($forwarder);
      } elsif ($dnst_programs[$array_index - 1] !~ m/pcap$/) {
        update_forwarder($forwarder);
      }

#Sumanth's pcap player commands 

      if($$configuration_ref{SYSTEM_CONFIG}{PCAPPLAYER} ne "JAVASERVER" && $$configuration_ref{SYSTEM_CONFIG}{PCAPPLAYER} ne "JAVACLIENTSERVER") {
        print "INFO: Replaying with Sumanth's Pcap Player\n";
        push(@output_log,"Replaying with Sumanth's Pcap Player");
        $server_command = "/root/pcapplayer/dns-server.py -i $$configuration_ref{SYSTEM_CONFIG}{TUNS_MGMT_IP} -p 1234 -s $$configuration_ref{FORWARDERS}{PCAP_LISTENING_IP} -f $program_name";
        $client_command = ["/root/pcapplayer/client.py -i $$configuration_ref{SYSTEM_CONFIG}{TUNS_MGMT_IP} -p 1234 -s $$configuration_ref{SYSTEM_CONFIG}{DUT_LAN2_IP} -f $program_name"];
        $server_daemon="dns-server.py";
        $client_process= ["pcapplayer"];
        dnst_server_call($server_command,$server_daemon);
        dnst_client_call($client_command) if($status ne "error");
      } elsif($$configuration_ref{SYSTEM_CONFIG}{PCAPPLAYER} eq "JAVASERVER") {

#Java player in server mode

          print "INFO: Replaying with JAVA Pcap player with Server command mode\n";
	  push(@output_log,"INFO: Replaying with JAVA Pcap player with Server command mode");
          $server_command = "/root/jre-1.8.0/bin/java -cp \"analytics-app-1.0.jar:spark-assembly-1.3.0-hadoop1.0.4.jar\" com.infoblox.analytics.pcapserverclient.PcapServerClient /root/$program_name $$configuration_ref{FORWARDERS}{PCAP_LISTENING_IP} $$configuration_ref{SYSTEM_CONFIG}{DUT_LAN1_IP}";
          dnst_server_call($server_command);
      } elsif($$configuration_ref{SYSTEM_CONFIG}{PCAPPLAYER} eq "JAVACLIENTSERVER") {

#Java player in client server mode

          print "INFO: Replaying with JAVA Pcap Player with Client Server command  mode\n";
	  push(@output_log,"INFO: Replaying with JAVA Pcap player with Clent Server command mode");
          $server_command = "/root/jre-1.8.0/bin/java -cp \"analytics-app-1.0.jar:spark-assembly-1.3.0-hadoop1.0.4.jar\" com.infoblox.analytics.pcapserverclient.PcapServerClient /root/$program_name $$configuration_ref{FORWARDERS}{PCAP_LISTENING_IP} $$configuration_ref{SYSTEM_CONFIG}{TUNC_LAN_IP}";
          $server_daemon="PcapServerClient";
          $client_command = ["/root/jre-1.8.0/bin/java -cp \"analytics-app-1.0.jar:spark-assembly-1.3.0-hadoop1.0.4.jar\" com.infoblox.analytics.pcapserverclient.PcapServerClient /root/$program_name $$configuration_ref{SYSTEM_CONFIG}{TUNC_LAN_IP} $$configuration_ref{SYSTEM_CONFIG}{DUT_LAN2_IP}"];
          $client_process= ["PcapServerClient"];
          dnst_server_call($server_command,$server_daemon);
          dnst_client_call($client_command) if($status ne "error");
      }
    } else {

#DNS Tunneling programs

      $server_command=$$configuration_ref{$program_name}{server_command};
      if (ref($$configuration_ref{$program_name}{client_commands}) eq "ARRAY") {
	 $client_command= [@{$$configuration_ref{$program_name}{client_commands}}];
      } else {
	 $client_command= [$$configuration_ref{$program_name}{client_commands}];
      }
      if (ref($$configuration_ref{$program_name}{client_processes}) eq "ARRAY") {
         $client_process= [@{$$configuration_ref{$program_name}{client_processes}}];
      } else {
         $client_process= [$$configuration_ref{$program_name}{client_processes}];
      }

#Substitue Variables data read from Configuration.xml file  

      if($server_command =~ m/(\b[A-Z][A-Z][A-Z].*?)\s/) {
        my @c = $server_command =~ /(\b[A-Z][A-Z][A-Z].*?)\s/g;
        my $count = @c;
        foreach(@c) {
          $val=$_;
          $server_command =~ s/$val/$$configuration_ref{SYSTEM_CONFIG}{$val}/ if(defined($$configuration_ref{SYSTEM_CONFIG}{$val}));
          $server_command =~ s/$val/$$configuration_ref{FORWARDERS}{$val}/ if(defined($$configuration_ref{FORWARDERS}{$val}));
        }
      }
      $server_daemon =$$configuration_ref{$program_name}{server_daemon} ;  
      my $listener= $program_name . "_LISTENING_IP";
      add_forward_zone($$configuration_ref{$program_name}{forward_zone_name}, $$configuration_ref{SYSTEM_CONFIG}{DUT_LAN1_IP}, $$configuration_ref{SYSTEM_CONFIG}{DUT_FQDN}, $$configuration_ref{FORWARDERS}{$listener}, $$configuration_ref{SYSTEM_CONFIG}{TUNS_FQDN});

# Add IT DNS resolver as global forwarder

      $forwarder=["10.102.3.10"];
      #$forwarder=[$$configuration_ref{FORWARDERS}{$listener}];
      update_forwarder($forwarder);
      dnst_server_call($server_command,$server_daemon);
      dnst_client_call($client_command) if($status ne "error");
      remove_forward_zone($$configuration_ref{$program_name}{forward_zone_name}); 
    }

#Clear DNS cache

    clear_dns_cache() if($program_name =~ m/pcap$/);

#Update the test case status

    testcase_status_update($status);

#Save all the test cases status 

    if($status eq "error") {
      $output_summary{$_}{result}="FAILED";
      $output_summary{$_}{time_elapsed}=0;
      $output_summary{$_}{blacklistdomains}=$blacklists;
      $output_summary{$_}{bugid}=$$configuration_ref{BUGS}{$_} if(exists($$configuration_ref{BUGS}{$_}));
      $output_summary{$_}{bugid}="" if(!exists($$configuration_ref{BUGS}{$_}));
      $output_summary{$_}{error_log}=[@error_log];

    } elsif($status ne "error"){
      $output_summary{$_}{result}="PASSED";
      $output_summary{$_}{time_elapsed}=$time_elapsed;
      $output_summary{$_}{blacklistdomains}=$blacklists;
      $output_summary{$_}{bugid}=" ";
    }
      $output_summary{$_}{output_log}=[@output_log];
      $output_summary{$_}{confidence}=$max_confidence;
    close(FH);
    sleep(15);
    $array_index++;
    my $testcase_end_time=time();
    my $test_case_duration=$testcase_end_time-$testcase_start_time;
    $output_summary{$_}{testcase_duration}=$test_case_duration;
  }
}

##############################################################################################
## Create API session                                                                        #
##############################################################################################

sub create_session
{
  $session = Infoblox::Session->new('master'=>$grid_master_ip, 'username'=>'admin', 'password'=>'infoblox');
  unless ($session) {
    die("Construct session failed: ",
        Infoblox::status_code() . ":" . Infoblox::status_detail());
  }
}

##############################################################################################
## Start the daemon on the the DNS tunneling server                                          #
##############################################################################################

sub dnst_server_call
{
  my $server_command=shift;
  my $seconds;
  my $process_completed=0;
  $blacklists=" ";
  if($program_name =~ m/pcap$/ && $$configuration_ref{SYSTEM_CONFIG}{PCAPPLAYER} eq "JAVASERVER") {
    my $blacklist_present=0;
    @blacklist_domains=();
    get_timestamps();
    
    my $blacklist_domain;
    my $m=1;
    $m=9 if($whitelist_flag);
    my $out =`ssh $SSH_FLAGS root\@$$configuration_ref{SYSTEM_CONFIG}{TUNS_MGMT_IP} $server_command > foos.out 2> foos.err < /dev/null &`;
    print "INFO: Replaying the pcap $program_name on Server and initiating the tunneling traffic...\n";
    push(@output_log,"INFO: Replaying the pcap $program_name on Server and initiating the tunneling traffic...");

    while($m<=12)
    {
       $seconds=$m*10;
       $m++;
       sleep(10);
       my $is_process_running=is_server_daemon_running("PcapServerClient");
       if(!$is_process_running) {
	 print "INFO: Pcap player execution got completed in ~$seconds seconds\n";
	 push(@output_log,"INFO: Pcap player execution got completed in ~$seconds seconds");
	 $m=13;
       } 
       $process_completed=1 if($m==13);
       next if(!$process_completed); 
       $blacklist_domain=validate_blacklist_domain_in_syslog(); 
       foreach(@{$blacklist_domain}) {
         if(($$blacklist_domain[0] ne "Not found")  && ($blacklist_present ==0)) {
           print "INFO: Blacklist domain found in DB\n"; 
	   push(@output_log,"INFO: Blacklist domain found in DB");
	   $blacklist_present=1;
	   kill_server_daemon("PcapServerClient"); 
	   sleep(5);
	   $blacklists=join(",",@{$blacklist_domain});
	   chomp($blacklists);
	   delete_blacklistdomain(@{$blacklist_domain});
	   $m=13;
	   #$status="error" if($whitelist_flag);
	   $status="error" if($whitelist_flag);
           $status="error" if($negative_test);
	   print "ERROR: This program is defined part of whitelist and blacklist domains added into RPZ when it shouldn't\n" if($whitelist_flag); 
	   print "ERROR: Blacklist domain added when it's not expected(negative testcase)\n" if($negative_test); 
	   push(@output_log,"ERROR: This program is defined part of whitelist and blacklist domains added into RPZ when it shouldn't") if($whitelist_flag);
           push (@error_log,"ERROR: This program is defined part of whitelist and blacklist domains added into RPZ when it shouldn't") if($whitelist_flag);
	   push(@output_log,"ERROR: Blacklist domain added when it's not expected") if($negative_test);
           push (@error_log,"ERROR: Blacklist domain added when it's not expected") if($negative_test);
           $status="error" if(!$match_found);
	   analytics_logs_details();
	  } 
      }
    }
    if(!$blacklist_present) {
      if($retry < 7 && (!$whitelist_flag && !$negative_test))
      {
         kill_server_daemon("PcapServerClient"); 
         sleep(10);
         clear_dns_cache() if ($program_name ne "iodine_direct_A.pcap");
         sleep(15) if ($program_name ne "iodine_direct_A.pcap");
         $retry++;
         print STDOUT "INFO: Retry $retry ........ \n";
	 push(@output_log,"INFO: Retry $retry .......");
         dnst_server_call($server_command); 
      } else {
         print STDOUT "INFO: Waited for $seconds seconds and the black domain is not present in the database\n";
	 push(@output_log,"INFO: Waited for $seconds seconds and the black domain is not present in the database");
	 print "ERROR: Blacklist domain NOT found in DB \n" if(!$whitelist_flag);
	 push (@output_log,"ERROR: Blacklist domain NOT found in DB") if(!$whitelist_flag); 
	 push (@error_log,"ERROR: Blacklist domain NOT found in DB") if(!$whitelist_flag); 
	 print "INFO: Blacklist domain NOT found in DB \n" if($whitelist_flag);
	 $status="error" if($whitelist_flag==0 && $negative_test==0 );
	 #$status="error" if(!$negative_test);
	 print "INFO: This program is defined part of whitelist and blacklist domain is not added into RPZ as expected\n" if($whitelist_flag); 
	 push(@output_log,"INFO: This program is defined part of whitelist and blacklist domain is not added into RPZ as expected") if($whitelist_flag);
	 print "INFO: It's a negative test case and blacklist domain is not added into RPZ as expected\n" if($negative_test); 
	 push(@output_log,"INFO: It's a negative test case and blacklist domain is not added into RPZ as expected") if($negative_test);
	 kill_server_daemon("PcapServerClient"); 
	 sleep(5);
	 analytics_logs_details();
      }
    }
  `cat foos.out >> $redirect_file`;
  `cat foos.err >> $redirect_file`;
  } else {
    my $daemon_process=shift;
#Get latest syslog and current time
    get_timestamps();
    my $is_process_running=is_server_daemon_running($daemon_process);
    if($is_process_running) {
      print "INFO: Server daemon $daemon_process is running on server\n";
      push(@output_log,"INFO: Server daemon $daemon_process is running on server");
      return;
    } 
    print "INFO: .... Initiating the Server daemon process .... \n";
    push(@output_log,"INFO: .... Initiating the Server daemon process ....");
    my $out=`ssh root\@$$configuration_ref{SYSTEM_CONFIG}{TUNS_MGMT_IP} $SSH_FLAGS $server_command > foos.out 2> foos.err < /dev/null &`;
    sleep(4);
    $is_process_running=is_server_daemon_running($daemon_process);
    if($is_process_running) {
      print "INFO: Server daemon $daemon_process is running on server\n";
      push(@output_log,"INFO:INFO: Server daemon $daemon_process is running on server ");
    } 
    `cat foos.out >> $redirect_file`;
    if(!$is_process_running) {
      print "ERROR: Unable to initiate the Server process, please check the configurations  ....  \n";
      push(@output_log,"ERROR: Unable to initiate the Server process, please check the configurations  ....");
      push(@error_log,"ERROR: Unable to initiate the Server process, please check the configurations  ....");
      $status="error"; 
      `cat foos.err >> $redirect_file`;
    }
  }
}

##############################################################################################
## Execute the commands on DNS Tunneling client to initiate the traffic and                  #
## validate the blacklist domain entry                                                       #
##############################################################################################

sub dnst_client_call
{
  @blacklist_domains=();
  my $client_commands=shift;
  my $blacklist_present=0;
  my ($blacklist_domain,$is_client_process_running);
  my $m=0;
  $m=3 if($whitelist_flag);
  my $ssh_command = "ssh root\@$$configuration_ref{SYSTEM_CONFIG}{TUNC_MGMT_IP} -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null";
  my $length=scalar(@{$client_commands});
  if($program_name =~ m/pcap$/) {
    my $out =`ssh $SSH_FLAGS root\@$$configuration_ref{SYSTEM_CONFIG}{TUNC_MGMT_IP} $$client_commands[0] > fooc.out 2> fooc.err < /dev/null &`;
    if ($out ne '') {`cat fooc.err >> $redirect_file`;die("Had some problem running pcap $program_name.  The output was\n$out\n"); }
    print "INFO: Replaying the pcap $program_name on client and initiating the tunneling traffic...\n";
    push(@output_log,"INFO: Replaying the pcap $program_name on client and initiating the tunneling traffic...");
    sleep(2);

    while($m<4)
    {
       sleep(30);
       $blacklist_domain=validate_blacklist_domain_in_syslog(); 
       foreach(@{$blacklist_domain}) {
         if(($$blacklist_domain[0] ne "Not found")  && ($blacklist_present ==0)) {
           print "INFO: Blacklist domain found in DB ... terminating the client pcapplayer process\n"; 
           push(@output_log,"INFO: Blacklist domain found in DB ... terminating the client pcapplayer process"); 
           $blacklist_present=1;
           $is_client_process_running=is_client_process_running("pcapplayer");
           if($is_client_process_running) {
             kill_client_process($client_process);
           }
	   kill_server_daemon($server_daemon); 
           sleep(5);
           $blacklists=join(",",@{$blacklist_domain});
           chomp($blacklists);
           delete_blacklistdomain(@{$blacklist_domain});
           $m=4;
           $status="error" if($whitelist_flag);
           print "ERROR: This program is defined part of whitelist and blacklist domains added into RPZ when it shouldn't\n" if($whitelist_flag); 
           push(@output_log,"ERROR: This program is defined part of whitelist and blacklist domains added into RPZ when it shouldn't") if($whitelist_flag); 
           push(@error_log,"ERROR: This program is defined part of whitelist and blacklist domains added into RPZ when it shouldn't") if($whitelist_flag); 
           $status="error" if(!$match_found);
        } 
      }
      $m++;
    }
    if(!$blacklist_present) {
      print STDOUT "INFO: Waited for two minutes and the black domain is not present in the database \n";
      push(@output_log,"INFO: Waited for two minutes and the black domain is not present in the database");
      print "INFO: Blacklist domain NOT found in DB \n" if($whitelist_flag);
      push(@output_log,"INFO: Blacklist domain NOT found in DB") if($whitelist_flag);
      print "ERROR: Blacklist domain NOT found in DB \n" if(!$whitelist_flag);
      push(@output_log,"ERROR: Blacklist domain NOT found in DB") if(!$whitelist_flag);
      push(@error_log,"ERROR: Blacklist domain NOT found in DB") if(!$whitelist_flag);
      $is_client_process_running=is_client_process_running("pcapplayer");
      if($is_client_process_running) {
        kill_client_process($client_process);
        }
      kill_server_daemon($server_daemon); 
      sleep(5);
      $status="error" if(!$whitelist_flag);
      print "INFO: This program is defined part of whitelist and blacklist domain is not added into RPZ as expected\n" if($whitelist_flag); 
      push(@output_log,"INFO: This program is defined part of whitelist and blacklist domain is not added into RPZ as expected") if($whitelist_flag); 
     }

#Copy the execution commands to redirect file 
    `cat fooc.out >> $redirect_file`;
    return;
  } else { 
    $i=0;
    my $x;
    $val="";
    my $sshlogin_check="";
    my $exp = Expect->spawn($ssh_command) or die "Cannot spawn $ssh_command: $!\n";
    $exp->log_stdout(0);
    $exp->log_file($redirect_file);
    while($i<$length) 
      {
	if($$client_commands[$i] =~ m/(\b[A-Z][A-Z][A-Z].*?)\s/) {
	  my @c = $$client_commands[$i] =~ m/(\b[A-Z][A-Z][A-Z].*?)\s/g;
	  my $count = @c;
	  foreach $x (@c)
	  {
	     $val=$x;
	     $$client_commands[$i] =~ s/$val/$$configuration_ref{SYSTEM_CONFIG}{$val}/ if($val ne "CNAME" && $val ne "TXT"  && $val ne "SRV"  && $val ne "MX"  && $val ne "A" && $val ne "DNScatClient");
	  }
	}
        $m=0;
        my $cliComplete=0;
        my @ssh_status;
        my $timeout=30;
        while(!$cliComplete) 
	  {
             $exp->expect(
             $timeout,
             [ qr/root.*/       => sub {  my $self = shift;
                                            print STDOUT "INFO: Running \'$$client_commands[$i]\' on the client\n";  
                                            my $client_command_junit_format=$$client_commands[$i];
					    if($client_command_junit_format =~ m/\&/) { 
					      $client_command_junit_format=~ s/\&//g;
					    } 
                                            push(@output_log,"INFO: Running \'$client_command_junit_format\' on the client");  
                                            $self->send("$$client_commands[$i]\r");
					    if($$client_commands[$i] =~ m/ssh/ && $$client_commands[$i] !~ "&" ) {
                                                select STDOUT;
					        @ssh_status = $self->expect(5);
						$sshlogin_check=$ssh_status[$i] || "";
						if ($sshlogin_check=~ m/Last login:.*?from.*/) {
						    print STDOUT "INFO: SSH login from client to Server is successful\n";
						    push(@output_log,"INFO: SSH login from client to Server is successful");
						    sleep(60);
						    $self->send("exit\r");
						}
					    }	
					    sleep(30) if($$client_commands[$i] !~ "&" );
				            sleep(5) if($$client_commands[$i] =~ "&" );
                                            $i++;
					    if($i != $length)  {
					      $cliComplete=1;
					      return;
					    } 
					    $blacklist_domain=validate_blacklist_domain_in_syslog(); 
					    foreach(@{$blacklist_domain}) {
					      if(($$blacklist_domain[0] ne "Not found")  && ($blacklist_present ==0)) {
					        print "INFO: Blacklist domain found in DB ... skipping subsequent commands execution\n"; 
						push(@output_log,"INFO: Blacklist domain found in DB ... skipping subsequent commands execution"); 
						$blacklist_present=1;
						kill_client_process($client_process);
						kill_server_daemon($server_daemon); 
						sleep(5);
						$blacklists=join(",",@{$blacklist_domain});
						chomp($blacklists);
						delete_blacklistdomain(@{$blacklist_domain}) if(!$move_to_whitelist_flag);
                                                $status="error" if($whitelist_flag);
						print "ERROR: This program is defined part of whitelist and blacklist domains added into RPZ when it shouldn't\n" if($whitelist_flag); 
                                                $status="error" if(!$match_found);
                                                analytics_logs_details();
					      } 
					    }
                                            sleep(5);
                                            $cliComplete=1;
                                       } ],
             );
          }
       # $i++;
      }
    $exp->send("exit\r");
    $exp->soft_close();
    select STDOUT;
    if(!$blacklist_present) {
      print "INFO: Blacklist domain is not found\n";
      push(@output_log,"INFO: Blacklist domain is not found");
      push(@error_log,"ERROR: Blacklist domain is not found") if($whitelist_flag); 
      kill_client_process($client_process);
      kill_server_daemon($server_daemon); 
      sleep(5);
      analytics_logs_details();
      $status="error" if(!$whitelist_flag);
      print "INFO: This program is defined part of whitelist and blacklist domain is not added into RPZ as expected\n" if($whitelist_flag); 
      push(@output_log,"INFO: This program is defined part of whitelist and blacklist domain is not added into RPZ as expected") if($whitelist_flag); 
    }
    if($move_to_whitelist_flag == 1 && $status ne "error" && $blacklist_present == 1) {
      move_blacklist_to_whitelist(@{$blacklist_domain});
      push(@whitelist_domains,@{$blacklist_domain});
      sleep(50);
    }
  } 
}

##############################################################################################
## Check if RPZ blacklist entry is present in DB                                             #
##############################################################################################

sub is_rpz_blacklistdomain_present
{

  my $blackdomain_name=shift;
  my @retrieved_objs = $session->search(
    object => "Infoblox::DNS::RPZRecord::CNAME",
    name   => $blackdomain_name,
    view   => "default" );
  my $response=$retrieved_objs[0];
  if($response)
  {
     print "INFO: Blacklist domain \'$$response{name}\' found in DB\n";
     push(@output_log,"INFO: Blacklist domain \'$$response{name}\' found in DB");
     return 1;
  } else {
      return 0;
    }
}  

##############################################################################################
## Delete the RPZ blacklist domain                                                           #
##############################################################################################

sub delete_blacklistdomain
{
  my @y;
  my @blacklistdomain_name=@_;
  my $fqdn=$blacklistdomain_name[0];
  my $x=@y=split(/\./,$fqdn);
  my $domain=$y[-2] . "." . $y[-1];
  foreach(@blacklistdomain_name) {
    print "INFO: Deleting the blacklist domain: $_ \n";
    push(@output_log,"INFO: Deleting the blacklist domain: $_ ");
    $_=~s/\*/\\*/;
    $j=0;
    my @retrieved_objs = $session->search(
      object => "Infoblox::DNS::RPZRecord::CNAME",
      name   => $_,
      view   => "default" );
  while($j<scalar(@retrieved_objs)) 
    {
      my $response = $session->remove( $retrieved_objs[$j] );
      $j++;
      unless ($response) { print "ERROR: Delete blacklist domain failed: ", Infoblox::status_code() . ":" . Infoblox::status_detail() . "\n"; $status="error"; }
    }
  }
# Delete the rpz blacklist domains if it's get re-added
  sleep(8);
  $j=0;
  my @retrieved_objs = $session->search(
      object => "Infoblox::DNS::RPZRecord::CNAME",
      name   => $domain,
      view   => "default" );
  while($j<scalar(@retrieved_objs))
    {
      print "\nINFO: === Deleting the re-added blacklist domain ==== \n";
      my $response = $session->remove( $retrieved_objs[$j] );
      $j++;
      unless ($response) { print "ERROR: Delete blacklist domain failed: ", Infoblox::status_code() . ":" . Infoblox::status_detail() . "\n"; }
    }
}

##############################################################################################
## Kill the server daemon process                                                            #
##############################################################################################

sub kill_server_daemon
{
  my $dnst_tool_daemon=shift;
  my $pid=`ssh $SSH_FLAGS root\@$$configuration_ref{SYSTEM_CONFIG}{TUNS_MGMT_IP} ps ax | grep \"$dnst_tool_daemon\" | grep -v grep | head -1 |  awk '{print \$1}' 2>/dev/null`;
  chomp($pid);
  if($pid =~ m/(\d+)/) {
    #print "DEBUG: Server daemon $dnst_tool_daemon is running on server with pid:$pid... Killing the server daemon process\n";
    `ssh $SSH_FLAGS root\@$$configuration_ref{SYSTEM_CONFIG}{TUNS_MGMT_IP} kill -9 $pid 2>/dev/null`;
  } else {
    print  "INFO: Killing the process: Server daemon $dnst_tool_daemon is not running on the server.. nothing to do \n";
    push(@output_log,"INFO: Killing the process: Server daemon $dnst_tool_daemon is not running on the server.. nothing to do");
  }
}

##############################################################################################
## Kill the Client proces                                                                    #
##############################################################################################

sub kill_client_process
{
  my $client_processes=shift;
  foreach(@{$client_processes}) {
    my $dnst_tool_process="$_"; 
    my $pid=`ssh $SSH_FLAGS root\@$$configuration_ref{SYSTEM_CONFIG}{TUNC_MGMT_IP} ps ax | grep \"$dnst_tool_process\" | grep -v grep | head -1 |  awk '{print \$1}' 2>/dev/null`;
    chomp($pid);
    if($pid =~ m/(\d+)/) {
      #print "DEBUG: Client process $dnst_tool_process is running on client with pid:$pid... Killing the client process\n";
      `ssh $SSH_FLAGS root\@$$configuration_ref{SYSTEM_CONFIG}{TUNC_MGMT_IP} kill -9 $pid 2>/dev/null`;
    } else {
      print  "INFO: Killing the process: Client daemon $dnst_tool_process is not successful or the command execution is completed \n";
      push(@output_log,"INFO: Killing the process: Client daemon $dnst_tool_process is not successful or the command execution is completed");
    }
  }
}

##############################################################################################
## Check if the daemon running on the Tunneling server                                       #
##############################################################################################

sub is_server_daemon_running
{
  my $dnst_tool_daemon=shift;
  my $pid=`ssh $SSH_FLAGS root\@$$configuration_ref{SYSTEM_CONFIG}{TUNS_MGMT_IP} ps ax | grep \"$dnst_tool_daemon\" | grep -v grep | head -1 |  awk '{print \$1}' 2>/dev/null`;
  chomp($pid);
  if($pid =~ m/(\d+)/) {
    #print "INFO: Server daemon $dnst_tool_daemon is running on server with pid:$1\n" if(!$$configuration_ref{SYSTEM_CONFIG}{PCAPPLAYER} eq "JAVASERVER"); 
    return 1;
  } else {
    #print  "INFO: Server daemon $dnst_tool_daemon is not running on the server \n" if(!$$configuration_ref{SYSTEM_CONFIG}{PCAPPLAYER} eq "JAVASERVER");
    return 0;
  }
}

##############################################################################################
## Check if process is running on the Tunneling Client                                       #
##############################################################################################

sub is_client_process_running
{
  my $dnst_tool_process=shift;
  my $pid=`ssh $SSH_FLAGS root\@$$configuration_ref{SYSTEM_CONFIG}{TUNC_MGMT_IP} ps ax | grep \"$dnst_tool_process\" | grep -v grep | head -1 |  awk '{print \$1}' 2>/dev/null`;
  chomp($pid);
  if($pid =~ m/(\d+)/) {
    print "INFO: Client process $dnst_tool_process is running on client with pid:$1\n";
    return 1;
  } else {
    print  "INFO: Client process $dnst_tool_process is not running on the client \n";
    return 0;
  }
}

##############################################################################################
## Restart NIOS services                                                                     #
##############################################################################################

sub restart_services
{
  print "INFO: Restarting services \n";
  push(@output_log,"INFO: Restarting services ");
  $session->restart(
     delay_between_members => 4,
     force_restart => "true",
  );
sleep 35;
}

##############################################################################################
## Update Test case status                                                                   #
##############################################################################################

sub testcase_status_update
{
  my $tc_status=shift;
  print "INFO: Please see \'$redirect_file\' for pcap replay/program execution details\n";
  if($tc_status eq "error") {
    #print "ERROR: New failure, to be investigated\n" if(!exists($$configuration_ref{BUGS}{$_}));
    print "ERROR: Failed due to bug $$configuration_ref{BUGS}{$_}\n" if(exists($$configuration_ref{BUGS}{$_}));
    print "Test case $program_name status is: Failed\n\n\n";
  } else {
    print "Test case $program_name status is: Passed \n\n\n";
 }
}

##############################################################################################
## Generate Junit reporting file                                                             #
##############################################################################################

sub generate_junit_report
{
  my $k=1;
  local $"="\n";
  my $length=scalar(keys(%output_summary));
  my $pass_count=0;
  my $fail_count=0;  
  foreach (@dnst_programs) 
  {
    $pass_count++ if ($output_summary{$_}{result} eq "PASSED");
    $fail_count++ if ($output_summary{$_}{result} eq "FAILED");
  }
  my $total_count=$pass_count + $fail_count;
  $current_time=`ssh root\@$grid_master_ip $SSH_FLAGS date +%FT%T`;
  my $end=time();
  my $time_diff=$end-$start;
  my $time_diff_in_minutes=ceil($time_diff/60);
#Generate xml file with all the data
  open(OF,">JUnitReport.xml");
  select OF;
  print qq(<?xml version="1.0" encoding="UTF-8"?>\n); 
  print qq(<testsuites>\n);
  print qq(\t<testsuite classname="DNS_TUNNELING" disabled="0" errors="0" failures="$fail_count" hostname="$$configuration_ref{SYSTEM_CONFIG}{DUT_FQDN}" id="1" name="DNS Tunneling PCAPS and PROGRAMS" package="" skipped="0" tests="$total_count" time="$time_diff" timestamp="$test_start_time">\n);
  print qq(\t\t<properties>\n);
  print qq(\t\t\t<property name="NIOS Version" value="$nios_version"/>\n);
  print qq(\t\t\t<property name="DNST detection threshold value" value="$$configuration_ref{SYSTEM_CONFIG}{DNST_DETECTION_THRESHOLD}"/>\n);
  print qq(\t\t\t<property name="PCAP Player" value="$$configuration_ref{SYSTEM_CONFIG}{PCAPPLAYER}"/>\n);
  print qq(\t\t\t<property name="Hardware Type" value="$hardware_type"/>\n);
  print qq(\t\t</properties>\n);
  foreach (@dnst_programs)
   {
     print qq(\t\t<testcase id="$k" classname="DNS_TUNNELING.PASS" name="$_" status="$output_summary{$_}{result}" time="$output_summary{$_}{testcase_duration}">\n) if($output_summary{$_}{result} eq "PASSED");
     print qq(\t\t<testcase id="$k" classname="DNS_TUNNELING.FAIL" name="$_" status="$output_summary{$_}{result}" time="$output_summary{$_}{testcase_duration}">\n) if($output_summary{$_}{result} eq "FAILED");
     print qq(\t\t\t<system-out>); 
     print qq(\t\t\t\t\t\t@{$output_summary{$_}{output_log}});
     print qq(\t\t\t</system-out>); 
     print qq(\t\t\t<failure message="@{$output_summary{$_}{error_log}} $output_summary{$_}{bugid}" type="ERROR"/>\n) if($output_summary{$_}{result} eq "FAILED");
     print qq(\t\t\t<properties>\n);
     print qq(\t\t\t\t<property name="Detection time" value="$output_summary{$_}{time_elapsed}"/>\n);
     print qq(\t\t\t\t<property name="Blacklist domains" value="$output_summary{$_}{blacklistdomains}"/>\n);
     print qq(\t\t\t</properties>\n);
     print qq(\t\t</testcase>\n);
     $k++;
   }
  print qq(\t</testsuite>\n);
  print qq(</testsuites>\n);
  close(OF);
  select STDOUT;
}

##############################################################################################
## Print Test execution summary                                                              #
##############################################################################################

sub print_summary
{
  my $c=1;
  my $k=0;
  my $row=7;
  local $"=",";
  my $dut_version="NIOS Version is: $nios_version";
  my $hardware_info="Hardware type: $hardware_type";
  my $pcapplayer_info="Pcap player: $$configuration_ref{SYSTEM_CONFIG}{PCAPPLAYER}\n";
  my $dut_dnst_threshold_info="DNST Detection threshold value is: $dut_dnst_threshold";
  my $dut_analytics_version_info="DNST Analytics engine version is : $dut_analytics_version";

#Excel code 

  my $xls_file= $myname . "_report" . "." . "xls";
  my $workbook = Spreadsheet::WriteExcel->new($xls_file);
  my $heading = $workbook->add_format(align => 'left', bold => 1);
  $heading->set_bg_color('yellow');
  my $worksheet = $workbook->add_worksheet("DNST Automation Report");
  my $format = $workbook->add_format();
  my $format2 = $workbook->add_format();
  my $format3 = $workbook->add_format();
  my $format4 = $workbook->add_format(align => 'right', bold => 1);
  my $format5 = $workbook->add_format(align => 'left', bold => 1);
  $format2->set_color('green');
  $format3->set_color('red');
  $format5->set_color('blue');
  $worksheet->set_column(0,0,85);
  $worksheet->set_column(1,1,10);
  $worksheet->set_column(2,2,90);
  $worksheet->set_column(3,3,25);
  $worksheet->set_column(4,4,10);
  $worksheet->set_column(5,5,25);
  $worksheet->write(0, 0, $dut_version,$format);
  $worksheet->write(1, 0, $dut_dnst_threshold_info,$format);
  $worksheet->write(2, 0, $dut_analytics_version_info,$format);
  $worksheet->write(3, 0, $hardware_info,$format);
  $worksheet->write(4, 0, $pcapplayer_info,$format);
  $worksheet->write(6, 0, 'Program Name',$heading);
  $worksheet->write(6, 1, 'Result',$heading);
  $worksheet->write(6, 2, 'Blacklistdomains',$heading);
  $worksheet->write(6, 3, 'Detection Time (~seconds)',$heading);
  $worksheet->write(6, 4, 'BUGS',$heading);
  $worksheet->write(6, 5, 'Classification Confidence',$heading);


  print "\n\n########################################\n";
  print "Test execution Summary \n"; 
  print "########################################\n";  
  my $length=scalar(keys(%output_summary));
  my $pass_count=0;
  my $fail_count=0;  
  foreach (@dnst_programs) 
  {
    my $pg_name;
    my $pcap_name;
    print "Test case $c: $dnst_programs[$k] : PASSED\n" if($output_summary{$_}{result} eq "PASSED"); 
    print "Test case $c: $dnst_programs[$k] : FAILED\n" if($output_summary{$_}{result} eq "FAILED"); 
    $pass_count++ if ($output_summary{$_}{result} eq "PASSED");
    $fail_count++ if ($output_summary{$_}{result} eq "FAILED");
    if($dnst_programs[$k] !~ m/pcap$/) {
      $pg_name= "$dnst_programs[$k]" . " (Tunneling program)"
    }
    if($dnst_programs[$k] !~ m/pcap$/ && $dnst_programs[$k] =~ m/rea_dnst/) {
      $pg_name= "$dnst_programs[$k]" . " (REA DNS)";
    }
    if ($dnst_programs[$k] !~ m/pcap$/ && ($dnst_programs[$k] ~~ @whitelist_domains)) {
       $pg_name= "$dnst_programs[$k]" . " (Tunneling program) (WHITELIST TEST) ";
    }
   if ($dnst_programs[$k] =~ m/pcap$/) {
       $pcap_name=$dnst_programs[$k];
    }
   if ($dnst_programs[$k] =~ m/pcap$/ && ("$dnst_programs[$k]" ~~ @whitelist_domains)) {
       $pcap_name= "$dnst_programs[$k]" . " (WHITELIST TEST) ";
    }

    $worksheet->write($row, 0, $pcap_name, $format) if($dnst_programs[$k] =~ m/pcap$/);
    $worksheet->write($row, 0, $pg_name, $format5) if($dnst_programs[$k] !~ m/pcap$/);
    $worksheet->write($row, 1, 'PASSED', $format2) if($output_summary{$_}{result} eq "PASSED");
    $worksheet->write($row, 1, 'FAILED', $format3) if($output_summary{$_}{result} eq "FAILED");
    $worksheet->write($row, 2, $output_summary{$_}{blacklistdomains}, $format);
    $worksheet->write($row, 3, $output_summary{$_}{time_elapsed}, $format);
    $worksheet->write($row, 4, $output_summary{$_}{bugid}, $format3);
    $worksheet->write($row, 5, $output_summary{$_}{confidence}, $format);
    $c++;
    $row++;
    $k++;
  }
  my $total_count=$pass_count + $fail_count;
  print "\n\nTotal number of test cases executed: $total_count \n"; 
  print "Number of test cases passed: $pass_count\n"; 
  print "Number of test cases failed: $fail_count\n"; 
  print "###########################################\n";
  $row++;
  $worksheet->write($row, 0, 'Total Executed', $format4);
  $worksheet->write($row, 1, $total_count, $format);
  $row++;
  $worksheet->write($row, 0, 'Total Passed', $format4);
  $worksheet->write($row, 1, $pass_count, $format2);
  $row++;
  $worksheet->write($row, 0, 'Total Failed', $format4);
  $worksheet->write($row, 1, $fail_count, $format3);
  $current_time=`ssh root\@$grid_master_ip $SSH_FLAGS date +%FT%T`;
  print "\nINFO: Test end time: $current_time\n";
  my $end=time();
  my $time_diff=$end-$start;
  my $time_diff_in_minutes=ceil($time_diff/60);
  print "\nINFO: Test execution duration: ~$time_diff_in_minutes minutes\n"; 
  $row++;
  $worksheet->write($row, 0, 'Test execution duration (~minutes)', $format4);
  $worksheet->write($row, 1, $time_diff_in_minutes, $format);
  print "\n\nPlease see \'$xls_file\' file for summarized report\n"; 
}

##############################################################################################
## Read the syslog file content and look for the domain                                      #
##############################################################################################

sub validate_blacklist_domain_in_syslog
{
  @syslog_content="";
  my ($detected_time,$black_domain);
  my $fmt="%Y-%m-%dT%H:%M:%S";
  my $ssh_command = "ssh root\@$ssh_ip -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null";
  my $exp = Expect->spawn($ssh_command) or die "Cannot spawn $ssh_command: $!\n";
  $exp->log_stdout(0);

  my $cliComplete=0;
  my $timeout=40;
  while(!$cliComplete) {
    $exp->expect(
            $timeout,
            [ qr/bash.*/       => sub {  my $exp = shift;
                                            $exp->send("sed -n '/$syslog_timestamp/,\$p' /var/log/syslog \r");
                                            #@syslog_content = $exp->expect(5);
					    $exp->expect(5);
					    my $text=$exp->before();
					    @syslog_content=split("\n",$text);
                                            $exp->send("exit\n\n");
                                            $cliComplete=1;
                                       } ],
    );
  }
  $exp->soft_close();

  foreach(@syslog_content)
    {
      if($_ =~ m/(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}).*?ZRQ applied ADD for '(.*?)': \d+ IN CNAME/) {
          print "INFO: Blackdomain $2 is added in RPZ\n";
          push(@output_log,"INFO: Blackdomain $2 is added in RPZ");
          $black_domain=$2;
          push(@blacklist_domains,$black_domain);
          $detected_time=$1;
          my $diff = Time::Piece->strptime("$detected_time",$fmt) - Time::Piece->strptime("$current_time",$fmt);
          $time_elapsed=$diff;
          print "INFO: Time elapsed for blackdomain addition into RPZ: ~$time_elapsed seconds\n";
          push(@output_log,"INFO: Time elapsed for blackdomain addition into RPZ: ~$time_elapsed seconds");
          $flag=1;
      }
      if($_ =~ m/DNS Tunneling/) {
          chomp($_);
          print "INFO: $_ \n";
      }
  }
  if(!$flag) {
    return \@str;
   } else {

# Validate the added domain against query domain

    my $match_positive=0;
    my $match_negative=0;
    foreach(@blacklist_domains)
    {
       my $pattern=$_;
       my $xml_pattern=$_;
       $pattern=~s/\*\./.*?query:.*?/;
       $xml_pattern=~s/\*\.//;
       my @matches="";
       @matches=grep /$pattern/,@syslog_content;
       print "INFO: Added RPZ blacklist domain \"$_\" is matching with query domains\n" if(scalar(@matches)>0); 
       push(@output_log,"INFO: Added RPZ blacklist domain $_ is matching with query domains") if(scalar(@matches)>0);
       $match_negative=1 if(scalar(@matches)==0);
       print "ERROR: Added RPZ blacklist domain $_ is NOT matching with query domains\n" if(scalar(@matches) == 0);
       push (@error_log,"ERROR: Added RPZ blacklist domain $xml_pattern is NOT matching with query domains\n") if(scalar(@matches) == 0);
       push (@output_log,"ERROR: Added RPZ blacklist domain $_ is NOT matching with query domains") if(scalar(@matches) ==0);
    }

   if ($match_negative == 0) {
   $match_found=1;
   } else {
    $match_found=0;
   }

  return \@blacklist_domains;
  }
}

##############################################################################################
## Copy the pcap file to tunneling server and client                                         #
##############################################################################################
sub pcap_file_copy
{
  my $ip=shift;
  my $filename=shift;
  my $scpstatus; 
  my $found=0;
  my $ssh = Net::OpenSSH->new($ip, user => "root", password => "infoblox", kill_ssh_on_timeout => 1, master_stderr_discard => 1, master_opts => [-o => "StrictHostKeyChecking=no"]);
  $ssh->error and die "Couldn't establish SSH connection: ". $ssh->error;
  my $output = $ssh->capture({stdin_discard => 0, stderr_to_stdout => 0},"cd;ls"); $ssh->error and   die "remote ls command failed: " . $ssh->error;
  $ssh->system("exit");
  my @values = split('\n', $output);
  foreach my $pcapfile (@values) {
    if($pcapfile eq $filename) {
      print "INFO: File $filename found on $ip\n";
      $found=1;
      last;
      }
  }
  if(!$found) {
    `scp "$path/$filename" root\@$ip\:\/root/`;
     print "INFO: File $filename is copied to $ip\n";
  }
}

##############################################################################################
## Add keys                                                                                  #
##############################################################################################

sub addkeys
{
    print "\nINFO: Calling addkeys $grid_master_ip ...\n";
    `addkeys $grid_master_ip`;
    if ($? == 0) {
      system("/usr/bin/ssh $SSH_FLAGS root\@$grid_master_ip date");
      if ($? == 0) {
        print "\nINFO: addkeys was successful.\n";
      } else {
         die " addkeys apparently failed.  If not using the grid's VIP (usually LAN, but maybe MGMT), then you have to do the addkeys yourself first.\n";
      }
    }
    sleep 20;
}

##############################################################################################
## Print test environment setup details                                                      #
##############################################################################################

sub test_env_details
{
  print "\nTest environment details ....\n";
  my $cmd_output=`ssh $SSH_FLAGS root\@$ssh_ip grep CLIENT_VERSION= /infoblox/config 2>/dev/null`;
  my ($hardware_id,$lab_id);
  if ($cmd_output =~ /CLIENT_VERSION=(.*)$/) {
    $nios_version=$1;
    print "INFO: NIOS Version is : $nios_version\n";
  } else {
    die "Could not determine NIOS version of $ssh_ip.  Command output was $cmd_output\n";
  }

  $hardware_type=`ssh $SSH_FLAGS root\@$ssh_ip cat /infoblox/var/hwtype.txt 2>/dev/null`;
  chomp $hardware_type;
  print "INFO: HWTYPE is : $hardware_type\n";
   
  if($hardware_type !~ m/VNIOS/) { 
    $hardware_id=`ssh $SSH_FLAGS root\@$ssh_ip cat /infoblox/var/hwtype.txt 2>/dev/null`;
    chomp $hardware_id;
    $cmd_output=`identify_lab_unit $hardware_id`;
    if ($cmd_output && $cmd_output =~ /$hardware_id is (.*)$/) {
      $lab_id=$1;
      print "INFO: Lab_ID is : $lab_id\n";
    } else {
      $lab_id='Unknown';
    }
  }
}

##############################################################################################
## Get Syslog and current time stamp for log validation                                      #
##############################################################################################
sub get_timestamps
{ 
  my $timestamp_syslog = `ssh root\@$ssh_ip $SSH_FLAGS tail -1 /var/log/syslog | cut -d' ' -f1`;
  chomp($timestamp_syslog);
  $syslog_timestamp=$timestamp_syslog;
#Get current system time
  $current_time=`ssh root\@$ssh_ip $SSH_FLAGS date +%FT%T`;
  my $timestamp_analytics_log= `ssh root\@$ssh_ip $SSH_FLAGS tail -1 /infoblox/var/analytics/logs/analytics.log | cut -d' ' -f1,2`;
  chomp($timestamp_analytics_log);
  $analytics_timestamp=$timestamp_analytics_log;
  $analytics_timestamp=~ s#\/#\\/#g; # Escape backslash character
}

##############################################################################################
## Clear DNS cache                                                                           #
##############################################################################################

sub clear_dns_cache
{
  print "INFO: Clearing DNS cache\n";
  push(@output_log,"INFO: Clearing DNS cache");
  $session->clear_dns_cache(
#     member => $ssh_ip,
     member => $$configuration_ref{SYSTEM_CONFIG}{DUT_LAN1_IP},
  );
 sleep(2);
}

##############################################################################################
## Update Grid forwarder settings                                                            #
##############################################################################################
sub update_forwarder
{
  my $forwarders=shift;
  my @result = $session->get(
  object => "Infoblox::Grid::DNS",
  name   => "Infoblox"
            );
  unless( @result ){
            die("Get grid DNS failed: ", $session->status_code() . ":" . $session->status_detail());
                   }
  my $grid_dns = $result[0];
  if ($grid_dns) {
    $grid_dns->forwarders([@{$forwarders}]);
    $grid_dns->forward_only('true');
  }
  $session->modify($grid_dns) or die("Modify grid DNS failed: ", $session->status_code() . ":" . $session->status_detail());
  print "INFO: Updating the global forwarders @{$forwarders}\n";
  push(@output_log,"INFO: Updating the global forwarders");
  sleep 2;
  restart_services();
}

##############################################################################################
## Update Analyticks parameter DNST threshold                                                #
##############################################################################################

sub set_dnst_detection_threshold
{
  my $timeout = 60;
  my $command = "ssh admin\@$ssh_ip -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null";
  my $exp = Expect->spawn($command) or die "Cannot spawn $command: $!\n";
  my $threshold_value=$$configuration_ref{SYSTEM_CONFIG}{DNST_DETECTION_THRESHOLD};
  my $threshold_command="set analytics_parameter member DNST dnst.detection.threshold $threshold_value"; 
  my $cliComplete=0;
  while(!$cliComplete) {
        $exp->expect(
           $timeout,
           [ qr/$usernamePrompt/       => sub { my $exp = shift;
                                                $exp->send("admin\n");
                                                exp_continue; } ],
           [ qr/$pwPrompt/             => sub { my $exp = shift;
                                                $exp->send("infoblox\n");
                                                exp_continue; } ],
           [ qr/Are you sure you want to continue connecting*/             => sub { my $exp = shift;
                                                                   $exp->send("yes\n");
                                                                    exp_continue; } ],
           [ qr/$prompt/               => sub { my $exp = shift;
                                                $exp->send("$threshold_command \n") ;
                                                sleep(7);
                                                $cliComplete=1;
                                               } ],
         );
    }
  $exp->soft_close();
  sleep(5);
  print "\n\n";
}

##############################################################################################
## Add Whitelist domains                                                                     #
##############################################################################################

sub add_whitelist_domains
{
  foreach(@_){
  my $whitelist = Infoblox::Grid::ThreatAnalytics::WhiteList->new(
        fqdn => "$_",
        comment => 'Added through API',
        disable => 'false',
     );

     #Submit for addition
  my $response = $session->add( $whitelist );
  unless ($response) { print "ERROR: Whitelist domain add failed: ", Infoblox::status_code() . ":" . Infoblox::status_detail() . "\n"; }
  if($response){
    print "INFO: Whitelist domain $_ added successfully\n";
    push(@output_log,"INFO: Whitelist domain $_ added successfully");
    }
  }
}

##############################################################################################
## Cleanup Whitelist domains                                                                     #
##############################################################################################

sub remove_whitelist_domains
{
  print "INFO: Removing the whitelist domains\n";
  foreach(@_){
    my $m=0;
    if($_ =~ /\*/) {
       $_=~ s/\*\.//; 
    }
    my @retrieved_objs = $session->get(
      object => "Infoblox::Grid::ThreatAnalytics::WhiteList",
      fqdn   => $_,
      );
    while($m<scalar(@retrieved_objs))
      {
        my $response = $session->remove( $retrieved_objs[$m] );
        $m++;
        unless ($response) { print "ERROR: Delete blacklist domain failed: ", Infoblox::status_code() . ":" . Infoblox::status_detail() . "\n"; $status="error"; }
      }
  }
}

##############################################################################################
## Unit configuration                                                                        #
##############################################################################################

sub initial_preparation
{
  print "INFO: Starting unit initial preparation\n";
  my $grid = $session->get(
     object => "Infoblox::Grid",
     name   => "Infoblox"
  );
 unless ($grid) {
     die("Get Grid failed: ", $session->status_code() . ":" . $session->status_detail());
  }
  $grid->remote_console_access("true");;
  $grid->support_access("true");
  $session->modify($grid) or die("Modify Grid failed: ", $session->status_code() . ":" . $session->status_detail());
  sleep 5;
  print "\nINFO: Enabling remote console and support access \n";
  restart_services();
 
  addkeys();
 
#Threat protection and Threat protection update temp license installation
  #install_rpz_license();
  sleep 50;
  #install_threat_analytics_license();
  sleep 50;

#Enable debug
  my $cmd_output=`ssh $SSH_FLAGS root\@$ssh_ip ls -l /infoblox/var/debug_analytics 2>/dev/null`;
  if ($cmd_output !~ /^-rw-rw-rw- .* \/infoblox\/var\/debug_analytics/) {
    system("/usr/bin/ssh $SSH_FLAGS root\@$ssh_ip touch /infoblox/var/debug_analytics");
    print localtime() . ": Restarting NIOS because I had to touch /infoblox/var/debug_analytics ...\n";
    system("/usr/bin/ssh $SSH_FLAGS root\@$ssh_ip /infoblox/rc restart 2>/dev/null");
    print localtime() . ": Waiting for $ssh_ip to come online after restarting product ...\n";

    my $start_time=time();            # Wait up to 5 minutes for the machine to answer pings.
    my $elapsed_time=0;
    while ($elapsed_time < 300) {
      `ping -nq -c 1 -W 2 $ssh_ip`;
      if ($? == 0) {last}

      $elapsed_time=time() - $start_time;
      if ($elapsed_time > 300) {
        print STDERR localtime() . ": waited too long for the $ssh_ip NIOS to come online.  Giving up.\n";
        exit 4;
      }

      print localtime() . ": still waiting for $ssh_ip to come back after restart.  It's been $elapsed_time seconds so far ...\n";
      sleep 2;
    }

    $elapsed_time=time() - $start_time;
    sleep 120;                                 # NIOS needs another few seconds to fully come back.
  }



  create_session();
#Enable DNS
  print "INFO: Enabling DNS Service \n";
  my $member_dns = $session->get(
  object => "Infoblox::Grid::Member::DNS",
    name   => "$$configuration_ref{SYSTEM_CONFIG}{DUT_FQDN}",
  );
  unless ($member_dns) {
    die("get member DNS failed: ", $session->status_code() . ":" . $session->status_detail());
  }
 $member_dns->enable_dns("true");
 $member_dns->use_mgmt_port("true") if(ref($$configuration_ref{SYSTEM_CONFIG}{DUT_MGMT_IP}) ne "HASH");
 $member_dns->use_lan2_port("true");
 $session->modify($member_dns) or die("DNS Service enable failed: ", $session->status_code() . ":" . $session->status_detail());
 
#Enable recursion, logging categories at Grid level
  print "INFO: Enabling recursion and logging\n";
  my @result = $session->get(
    object => "Infoblox::Grid::DNS",
    name   => "Infoblox"
            );
         unless( @result ){
            die("Get grid DNS failed: ", $session->status_code() . ":" . $session->status_detail());
                          }
  my $grid_dns = $result[0];
         if ($grid_dns) {
                         $grid_dns->allow_recursive_query("true");
                         $grid_dns->logging_categories(["general", "client", "config", "database", "dnssec", "lame_servers", "network", "notify", "queries", "resolver", "security", "update", "xfer_in", "xfer_out", "update_security", "queries", "responses", "rpz"]);
                         }
  $session->modify($grid_dns) or die("Modify grid DNS failed: ", $session->status_code() . ":" . $session->status_detail());
  sleep 5;
  
#Add RPZ zone

   print "INFO: Adding rpz zone \'$zone_name\' \n";
   my $memberns1 = Infoblox::DNS::Member->new(
    name     => "$$configuration_ref{SYSTEM_CONFIG}{DUT_FQDN}",
    ipv4addr => $$configuration_ref{SYSTEM_CONFIG}{DUT_LAN1_IP},
  );

  my $rpz_zone = Infoblox::DNS::Zone->new (
    name     => $zone_name,
    comment  => "Automation test zone",
    disable  => "false",
    rpz_policy => "GIVEN",
    primary => $memberns1,
  );

  $session->add($rpz_zone)
    or die("Add RPZ zone failed: ",
               $session->status_code(). ":" .$session->status_detail());

#Update Grid Analytics properties

  print "INFO: Updating mitigation rpz zone \'$zone_name\' in Grid Analytic properties\n"; 
  my @gridanalytics = $session->get(
     'object' => 'Infoblox::Grid::ThreatAnalytics',
 );
  my $grid_analytics = $gridanalytics[0];
         if ($grid_analytics) {
                         $grid_analytics->dns_tunnel_black_list_rpz_zone($rpz_zone);
                         }
  $session->modify($grid_analytics) or die("Modify grid Analytics failed: ", $session->status_code() . ":" . $session->status_detail());
  sleep 5;
  
#Start analytics service

  print "INFO: Starting Analytics services \n\n\n"; 
  my @analytics_member = $session->get(
     'object'      => 'Infoblox::Grid::ThreatAnalytics::Member',
     'name'        => "$$configuration_ref{SYSTEM_CONFIG}{DUT_FQDN}",
  );
  my $member=$analytics_member[0];
  $member->enable_service('true');
  $session->modify($member) or die("Enabling Analytics service action is failed: ", $session->status_code() . ":" . $session->status_detail());
  restart_services();
  sleep 15;
}

##############################################################################################
## Install RPZ license if not installed already                                              #
##############################################################################################

sub install_rpz_license
{
  my $cli_command = "ssh admin\@$ssh_ip -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null";
  my $exp = Expect->spawn($cli_command) or die "Cannot spawn $cli_command: $!\n";
  my $cliComplete=0;
  my $sub_prompt_count=0;
  my $prompt_count=0;
  my $timeout=60;
  while(!$cliComplete) {
        $exp->expect(
            $timeout,
            [ qr/$usernamePrompt/       => sub { my $exp = shift;
                                                $exp->send("admin\n");
                                                exp_continue; } ],
            [ qr/$pwPrompt/             => sub { my $exp = shift;
                                                $exp->send("infoblox\n");
                                                exp_continue; } ],
            [ qr/Are you sure you want to continue connecting*/             => sub { my $exp = shift;
                                                                         $exp->send("yes\n");
                                                                          exp_continue; } ],
             [ qr/$prompt/               => sub { my $exp = shift;
                                                  $prompt_count++;
						  if($prompt_count == 3) {
						    $exp->send("exit\n\n");
						    $cliComplete=1;
						    print "\nINFO: RPZ license installation is not required, already installed";
						    } elsif($prompt_count == 1) {
                                                    $exp->send("show license\n");
                                                    sleep(3);
                                                    my @options = $exp->expect(5);
                                                    license_check($options[3]);
                                                    if($rpz_license_flag) {
                                                      $exp->send("exit\n\n");
                                                      $cliComplete=1;
                                                      print "\n\nINFO: RPZ license is already installed\n";
                                                    }else {
                                                       $exp->send("set temp_license\n");
                                                       exp_continue;
                                                    }
                                                  }
                                                } ],

            [ qr/Are you sure you want to do this*/             => sub { my $exp = shift;
                                                                         $exp->send("y\n");
                                                                         $sub_prompt_count++;
                                                                         $exp->send("exit\n\n") if($sub_prompt_count == 2); 
                                                                         $cliComplete=1 if($sub_prompt_count == 2);
                                                                         exp_continue if($sub_prompt_count == 1); 
                                                                       } ],
            [ qr/Restart UI now*/             => sub { my $exp = shift;
                                                       $exp->send("y\n\n");
                                                       sleep(4);
						       #$exp->send("exit\n\n");
                                                       exp_continue;
                                                        } ],

            [ qr/Select license.*or q to quit*/     => sub { my $exp = shift;
                                                             my @options = $exp->before();
                                                             $options[0] =~ m/(\d+)\. Add Response Policy Zones license/;
                                                             $exp->send("$1\n");
                                                              exp_continue; } ],
                );
  }
  $exp->soft_close();
  sleep(60) if($sub_prompt_count == 2);
}

##############################################################################################
## Install Threat Analytics license                                                          #
##############################################################################################

sub install_threat_analytics_license
{
  my $cli_command = "ssh admin\@$ssh_ip -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null";
  my $exp = Expect->spawn($cli_command) or die "Cannot spawn $cli_command: $!\n";
  my $cliComplete=0;
  my $sub_prompt_count=0;
  my $prompt_count=0;
  my $timeout=60;
  while(!$cliComplete) {
        $exp->expect(
            $timeout,
            [ qr/$usernamePrompt/       => sub { my $exp = shift;
                                                $exp->send("admin\n");
                                                exp_continue; } ],
            [ qr/$pwPrompt/             => sub { my $exp = shift;
                                                $exp->send("infoblox\n");
                                                exp_continue; } ],
            [ qr/Are you sure you want to continue connecting*/             => sub { my $exp = shift;
                                                                         $exp->send("yes\n");
                                                                          exp_continue; } ],
             [ qr/$prompt/               => sub { my $exp = shift;
                                                  $prompt_count++;
                                                  if($prompt_count == 1) {
                                                    $exp->send("show license\n");
                                                    sleep(5);
                                                    my @options = $exp->expect(5);
                                                    license_check_threat_analytics($options[3]);
                                                    if($threat_analytics_license_flag) {
                                                      $exp->send("exit\n\n");
                                                      $cliComplete=1;
                                                      #print "\n\nINFO: Threat Analytics license is already installed\n";
                                                    }else {
                                                       $exp->send("set temp_license\n");
                                                       exp_continue;
                                                    }
                                                  }
                                                } ],

            [ qr/Are you sure you want to do this*/             => sub { my $exp = shift;
                                                                         $exp->send("y\n");
                                                                         $sub_prompt_count++;
                                                                         $exp->send("exit\n\n") if($sub_prompt_count == 2); 
                                                                         $cliComplete=1 if($sub_prompt_count == 2);
                                                                         exp_continue if($sub_prompt_count == 1); 
                                                                       } ],
            [ qr/Restart UI now*/             => sub { my $exp = shift;
                                                       $exp->send("y\n\n");
                                                       sleep(4);
						       #$exp->send("exit\n\n");
                                                       exp_continue;
                                                        } ],

            [ qr/Select license.*or q to quit*/     => sub { my $exp = shift;
                                                             my @options = $exp->before();
                                                             $options[0] =~ m/(\d+)\. Add Threat Analytics license/;
                                                             $exp->send("$1\n");
                                                              exp_continue; } ],
                );
  }
  $exp->soft_close();
  sleep(60) if($sub_prompt_count == 2);
}

##############################################################################################
## Do license install check                                                                  #
##############################################################################################

sub license_check
{
foreach (@_) {
 if ($_ =~ m/(Response Policy Zones)/) {
   print "\n\nINFO: RPZ license is already installed\n";
   $rpz_license_flag=1;
  }
 }
}


##############################################################################################
## Do threat analytics license install check                                                 #
##############################################################################################

sub license_check_threat_analytics
{
foreach (@_) {
  if ($_ =~ m/(Threat Analytics)/) {
   print "\n\n INFO: Threat Analytics license is already installed\n";
   $threat_analytics_license_flag=1;
  }
 }
}


##############################################################################################
## Move to whitelist test                                                                    #
##############################################################################################

sub move_to_whitelist
{
  @output_log="";
  print "INFO: Running move to whitelist test\n";
  push(@output_log,"INFO: Running move to whitelist test");
  my $forwarder;
  foreach (@move_to_whitelist_cases) 
  { 
    my $testcase_start_time=time(); 
    $status="successful";
    $redirect_file="$output_dir/$_._move_to_whitelist.log";
    $move_to_whitelist_flag=1;
    $program_name="$_";
    $server_command=$$configuration_ref{$program_name}{server_command};
    if (ref($$configuration_ref{$program_name}{client_commands}) eq "ARRAY") {
        $client_command= [@{$$configuration_ref{$program_name}{client_commands}}];
    } else {
       $client_command= [$$configuration_ref{$program_name}{client_commands}];
    }
    if (ref($$configuration_ref{$program_name}{client_processes}) eq "ARRAY") {
     $client_process= [@{$$configuration_ref{$program_name}{client_processes}}];
    } else {
     $client_process= [$$configuration_ref{$program_name}{client_processes}];
    }

#Substitute Variables data read from Configuration.xml file

  if($server_command =~ m/(\b[A-Z][A-Z][A-Z].*?)\s/) {
    my @c = $server_command =~ /(\b[A-Z][A-Z][A-Z].*?)\s/g;
    my $count = @c;
    foreach(@c) {
      $val=$_;
      $server_command =~ s/$val/$$configuration_ref{SYSTEM_CONFIG}{$val}/ if(defined($$configuration_ref{SYSTEM_CONFIG}{$val}));
      $server_command =~ s/$val/$$configuration_ref{FORWARDERS}{$val}/ if(defined($$configuration_ref{FORWARDERS}{$val}));
    }
  }
  $server_daemon =$$configuration_ref{$program_name}{server_daemon} ;
  my $listener= $program_name . "_LISTENING_IP";
  $forwarder=[$$configuration_ref{FORWARDERS}{$listener}];
  update_forwarder($forwarder);
  dnst_server_call($server_command,$server_daemon);
  dnst_client_call($client_command) if($status ne "error");
  if($status eq "error") {
      $program_name.="_move_to_whitelist_test";
      push(@dnst_programs,"$program_name");
      $output_summary{$program_name}{result}="FAILED";
      $output_summary{$program_name}{time_elapsed}=0;
      $output_summary{$program_name}{blacklistdomains}=$blacklists;
      $output_summary{$program_name}{bugid}="";
      $output_summary{$program_name}{error_log}=[@error_log];

#Clear DNS cache
      clear_dns_cache();
  } else  {
      sleep(20);
#Clear DNS cache
      clear_dns_cache();
      $whitelist_flag=1;
      $move_to_whitelist_flag++;
      dnst_server_call($server_command,$server_daemon);
      dnst_client_call($client_command) if($status ne "error"); 
      $program_name.="_move_to_whitelist_test";
      push(@dnst_programs,"$program_name");
      if($status eq "error") {
         $output_summary{$program_name}{result}="FAILED";
	 $output_summary{$program_name}{time_elapsed}=$time_elapsed;
	 $output_summary{$program_name}{blacklistdomains}=$blacklists;
	 $output_summary{$program_name}{bugid}="";
	 $output_summary{$program_name}{error_log}=[@error_log];
      } else {
         $output_summary{$program_name}{result}="PASSED";
         $output_summary{$program_name}{time_elapsed}=0;
         $output_summary{$program_name}{blacklistdomains}=$blacklists;
         $output_summary{$program_name}{bugid}="";
         $output_summary{$program_name}{error_log}=[@error_log];
      }
  }
  $output_summary{$program_name}{output_log}=[@output_log];
  testcase_status_update($status);
  my $testcase_end_time=time();
  my $test_case_duration=$testcase_end_time-$testcase_start_time;
  $output_summary{$program_name}{testcase_duration}=$test_case_duration;
  analytics_logs_details();
  $output_summary{$_}{confidence}=$max_confidence;
  }
  remove_whitelist_domains(@whitelist_domains) if(scalar(@whitelist_domains)>=1);
}

##############################################################################################
## TCP test cases                                                                            #
##############################################################################################

sub Rea_Dnst_query_test 
{
#Add REA DNS as global forwarder

  print "INFO: Executing REA_DNST_TEST_CASES\n\n"; 
  my $rea_dns_forwarder=["10.39.16.160"];
  update_forwarder($rea_dns_forwarder);
  my $blacklist_present=0;
  my $blacklist_domain;

#Add all the tcp test cases into an array   

  my @rea_test_cases=();

#Read all the rea_dnst test cases from Configuration xml file

  foreach (keys(%{$configuration_ref}))
  {
    if($_ =~ m/^rea_dnst/) {
      push(@rea_test_cases,$_); 
    }
  }

  foreach(@rea_test_cases) { 
    @blacklist_domains=();
    $blacklists="";
    @error_log="";
    @output_log="";
    $redirect_file="$output_dir/$_.log";
    open(OF,"> $redirect_file") or die "Could not write the test case details file.\n";
    my $testcase_start_time=time(); 
    $status="successful";
    $program_name="$_";
    push(@dnst_programs,$program_name); 
    print "INFO: Executing REA_DNST_TEST_CASE $program_name\n"; 
    $blacklist_present=0; 
    get_timestamps();
    sleep(1);
    my $query_command= "$$configuration_ref{$_}{query}";# Read from config file  
    my $expected= $$configuration_ref{$_}{expected}; # Expected result postive or negative
#Run the dig command
    $query_command =~ s/DUT_LAN1_IP/$$configuration_ref{SYSTEM_CONFIG}{DUT_LAN1_IP}/; 

    select OF;
    system("$query_command > fooq.out 2> fooq.err < /dev/null");
    sleep(20);
    select STDOUT;
    $blacklist_domain=validate_blacklist_domain_in_syslog(); 
    foreach(@{$blacklist_domain}) {
      if(($$blacklist_domain[0] ne "Not found")  && ($blacklist_present ==0)) {
         print "INFO: Blacklist domain found in DB\n";
         push(@output_log,"INFO: Blacklist domain found in DB");
         $blacklist_present=1;
         delete_blacklistdomain(@{$blacklist_domain});
         $blacklists=join(",",@{$blacklist_domain});
         }
       }
    if(!$blacklist_present) {
       if($expected eq "positive") {
           print STDOUT "ERROR: Black domain is not present in the database\n";
	   $status="error";
	   push(@output_log,"ERROR: Black domain is not present in the database");
	   push (@error_log,"ERROR: Blacklist domain NOT found in DB");
       } else {
           print STDOUT "INFO: Black domain is not present in the database as expected\n";
	   $status="successful";
	   print "INFO: Blacklist domain is not added into RPZ as expected\n";
	   push(@output_log,"INFO: Blacklist domain is not added into RPZ as expected");
       }
    }
    `cat fooq.out >> $redirect_file`;
    `cat fooq.err >> $redirect_file`;

    if($status eq "error") {
       $output_summary{$program_name}{result}="FAILED";
       $output_summary{$program_name}{time_elapsed}=0;
       $output_summary{$program_name}{blacklistdomains}=$blacklists;
       $output_summary{$program_name}{bugid}="";
       $output_summary{$program_name}{error_log}=[@error_log];
    } else {
       $output_summary{$program_name}{result}="PASSED";
       $output_summary{$program_name}{time_elapsed}=$time_elapsed;
       $output_summary{$program_name}{blacklistdomains}=$blacklists;
       $output_summary{$program_name}{bugid}="";
       $output_summary{$program_name}{error_log}=[@error_log];
    }
    analytics_logs_details();
    $output_summary{$program_name}{output_log}=[@output_log];

#Clear DNS cache
    clear_dns_cache();

    testcase_status_update($status);
    my $testcase_end_time=time();
    my $test_case_duration=$testcase_end_time-$testcase_start_time;
    $output_summary{$program_name}{testcase_duration}=$test_case_duration;
    $output_summary{$_}{confidence}=$max_confidence;
    close(OF);
  }
}
##############################################################################################
## Move black list domain to white list                                                      #
##############################################################################################

sub move_blacklist_to_whitelist
{

#Getting the DNS object from appliance through session.
   foreach(@_){
     my @result = $session->get(
       object => "Infoblox::Grid::ThreatAnalytics::Member",
       name   => "$$configuration_ref{SYSTEM_CONFIG}{DUT_FQDN}"
     );
     unless( @result ){
      die("Get grid DNS failed: ", $session->status_code() . ":" . $session->status_detail());
     }

  my $member = $result[0];
  my $blacklist_domain_name=$_ . "." . "$zone_name";
  print "INFO: Moving the blacklist domain to whitelist\n";

  my @retrieved_objs = $session->get(
    object => "Infoblox::DNS::RPZRecord::CNAME",
    name   => $blacklist_domain_name,
    );
  my $cname_obj = $retrieved_objs[0];
  my $response = $member->move_black_list_rpz_cnames_to_threat_analytics_whitelist($cname_obj);
  unless ($response) { print "ERROR: Move blacklist domain has failed: ", Infoblox::status_code() . ":" . Infoblox::status_detail() . "\n"; $status="error"; }
  }
}

##############################################################################################
## Get confidence value from the analytics.log file                                          #
##############################################################################################

sub analytics_logs_details
{
  @analytics_content="";
  @classification_confidence=();
  $max_confidence=0.0;
  my $ssh_command = "ssh root\@$ssh_ip -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null";
  my $exp = Expect->spawn($ssh_command) or die "Cannot spawn $ssh_command: $!\n";
  $exp->log_stdout(0);

  my $cliComplete=0;
  my $timeout=40;
  while(!$cliComplete) {
    $exp->expect(
            $timeout,
            [ qr/bash.*/       => sub {  my $exp = shift;
                                            $exp->send("sed -n '/$analytics_timestamp/,\$p' /infoblox/var/analytics/logs/analytics.log | grep -i Classification \r");
                                            $exp->expect(5);
                                            my $text=$exp->before();
                                            @analytics_content=split("\n",$text);
                                            $exp->send("exit\n\n");
                                            $cliComplete=1;
                                       } ],
    );
  }
  $exp->soft_close();
  foreach(@analytics_content)
    {
      if($_ =~ m/Classification confidence:\s(0.\d+)/) {
          print "INFO: Classification confidence: $1 \n"; 
          push(@classification_confidence,$1);
          push(@output_log,"INFO: Classification_confidence: $1");
      }
   }
  if(scalar(@classification_confidence) == 0) {
    $max_confidence= ""; 
  } else {
    $max_confidence= max @classification_confidence;
  }
}

##############################################################################################
## Remove the forward zone                                                                   #
##############################################################################################

sub remove_forward_zone
{
  my $zone_name=shift;
  my @result_array = $session->get(
     object => "Infoblox::DNS::Zone",
     name   => $zone_name,
  );
  my $zone = $result_array[0];
  $session->remove($zone)
     or die("Remove zone for $zone_name failed: ",
                $session->status_code(). ":" .$session->status_detail());

  print "INFO: Forward Zone $zone_name removed successfully.\n";
  restart_services();
}

##############################################################################################
## Add forward zone                                                                          #
##############################################################################################

sub add_forward_zone
{
  my ($zone_name, $nios_member_ip, $nios_member_fqdn, $forwarding_server_ip, $forwarding_server_fqdn)=@_;

#See if the zone already exists in the database

  my @result_array = $session->get(
     object => "Infoblox::DNS::Zone",
     name   => $zone_name,
  );
  my $zone = $result_array[0];
  if($zone){
    print "INFO: Forward Zone \'$zone_name\' already present in DB \n";
    return;
  }

  my $member = Infoblox::DNS::Nameserver->new(
        name     => "$forwarding_server_fqdn",
        ipv4addr => $forwarding_server_ip,
  );
  my $nameserver = Infoblox::DNS::Member->new(
        name     => $nios_member_fqdn,
        ipv4addr => $nios_member_ip,
   );

  my $fwd_zone = Infoblox::DNS::Zone->new(
     name        => $zone_name,
     comment     => "add forward zone $zone_name for pcap test",
     forward_to  => [$member],
     members     => [$nameserver],
     forward_only=> "true",
     );

  unless($fwd_zone){
        die("Construct $zone_name zone object failed: ",
                Infoblox::status_code(). ":" .Infoblox::status_detail());
        }

  $session->add($fwd_zone)
     or die("Add zone for $zone_name failed: ",
                $session->status_code(). ":" .$session->status_detail());

  print "INFO: Forward Zone $zone_name added successfully.\n";
#  restart_services();
}


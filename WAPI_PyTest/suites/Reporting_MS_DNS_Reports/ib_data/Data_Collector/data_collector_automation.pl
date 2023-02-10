#!/usr/bin/perl
use Time::Local;
use Getopt::Std;
use POSIX qw(strftime);
use Expect;
my $USAGE =<<USAGE;
     Usage:
       ./data_collector_lrt.pl -s <DC Server IP> -u <DC UserName> -p <DC Passwd> -r <min_pattern|min_pattern:max_pattern> -d <MM:DD:YYYY> -m <member name separated by ':'>

     Example:
       ./data_collector_lrt.pl -s 10.36.2.5 -u dc_user -p dc_pass -r 2000:10000 -d 1 -m member1.com:member2.com      #For Incremental Query pattern. (r 1000:20000)
       ./data_collector_lrt.pl -s 10.36.2.5 -u dc_user -p dc_pass -r 2000 -d 1 -m member3.com:member4.com            #For Static Query pattern.  ( -r 2000)

       -s : DC Server IP                                                                                             #Required
       -u : DC User name  , default 'admin'                                                                          #optional
       -p : DC Password   , default 'infoblox'                                                                       #optional 
       -r : User can specify static or variable range  , default will be static with value 2000                      #optional 
       -l : Duration in min, default value is 60 min                                                                 #Optional 
       -d : Date in MM:DD:YYYY format.                             default value is current date                    #Optional 
       -m : member names separated by ':'   default is 'lrt_test.com'                                                #Optional 
       -c : client ip

     Note:
       1. Query Rate Interval will be calculated based on following.
                Interval = (DURATION X 60) /( Max Pattern  /  Min Pattern )
                Example : if  -r 1000:10000  -d 720 ;  Then script will be execute 1 day with incremental load of 1000 pattern with interval of 4320 Sec., (i.e., every 72 min)
USAGE
#Created By : Raghavendra MN (rnagaraja@infoblox.com)
#Date : 02/09/2016

my %option = ();
getopts("s:u:p:r:d:h:c:", \%option);

if (defined($option{h})) {
  print "\n\n\n$USAGE\n\n\n";
  exit(0);
}
my $dc_server_ip;
if (!defined($option{s})){
   print "\n\nERROR: DC Server ip is required. Please check the help for script usage..\n\n";
   exit(0);  
}
else {
  $dc_server_ip = $option{s};
}

my $member    = (defined($option{m})) ? $option{m} : "lrt_test.com";
my $client    = (defined($option{c})) ? $option{c} : "10.20.30.40";
my $dc_user = (defined($option{u})) ? $option{u} : "admin";
my $dc_pass = (defined($option{p})) ? $option{p} : "infoblox";
my ($ini_qps,$max_qps) = (defined($option{r})) ? split(/:/,$option{r}):(2000,0);
print "************************** $ini_qps , $max_qps ****************";
my $iteration = (($max_qps eq '')||(int($max_qps) eq 0))? 'false':'true';
my $duration = (defined($option{l})) ? int($option{l})*60 : 3600;  #default will be 1 hour
my $inc_dur   = ($iteration eq 'true') ? int($duration/(int($max_qps)/int($ini_qps))) : $duration;
my $query_rate=$ini_qps;
my $schd_run_time = $duration + time;
system ("mkdir -p /tmp/already_copied_files"); 
#Loading files in 'Data Collector'
my $t=$inc_dur + time;
#foreach $client (@client_ip){
  load($member,$query_rate, $client);
  system("mv captured-dns-* /tmp/already_copied_files");
#  last if time > $schd_run_time;
#  if ( time > $t){
#    $t=$inc_dur + time;
#    $query_rate = (($query_rate + $ini_qps) < $max_qps )?$query_rate+$ini_qps:$max_qps ;
#  }
#}
system("rm -rf /tmp/already_copied_files"); #Removing '/tmp/already_copied_files' after completion of execution. 


sub load
{
my ($member,$pattern,$client) = @_;
my $member="ib-".join('-',split('\.',$client)).".infoblox.com";
#Generate Query File
if (!defined($option{d})){
  system("perl Capture_dns_query_generator_automation.pl -m $member -q $pattern  -c $client");
}
 else
{
  my $d = $option{d};
  system("perl Capture_dns_query_generator_automation.pl -m $member -q $pattern -d $d -c $client ");
}
#Creating MD5 File corresponding to Query Capture File
$dir = "*.gz";
my @files = glob( $dir );
foreach my $file (@files ){
 my $temp = `md5sum $file`;
    $temp =~ m/([a-zA-Z0-9]+)\s/;
    open(MD5,">$file.md5");
    $temp =~ m/([a-zA-Z0-9]+)\s/;
    print MD5 $1;
    close(MD5);

#Copy Query Capture File into 'Data Collector'. 
  my $exp         = Expect->new;
  my $timeout     = 200;
  my $password    = "$pass";
  $exp->raw_pty(1);
  $exp->spawn("scp $file $file.md5 $dc_user\@$dc_server_ip:")
        or die "Cannot Spawn Scp\n";
  $exp->expect($timeout,
                [
                    qr/Are you sure you want to continue connecting \(yes\/no\)?/i,
                    sub {
                          my $self = shift;
                          $self->send("yes\n");
                          exp_continue;
                        }
                ],
                [
                   qr/password:/i,
                    sub {
                          my $self = shift;
                          $self->send("$dc_pass\n");
                        }
                 ]
  );
  $exp->soft_close();
 }
}


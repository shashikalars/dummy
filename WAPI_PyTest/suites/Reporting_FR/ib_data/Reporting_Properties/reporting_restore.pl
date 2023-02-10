use strict;
use Infoblox;
use POSIX qw(strftime);
 my $host_ip           = $ARGV[0];
 my $restore_host      = $ARGV[1];  #which is defined in config.py
 my $scp_user          = $ARGV[2];  #which is defined in config.py
 my $scp_passwd        = $ARGV[3];  #which is defined in config.py
 my $restore_directory = $ARGV[4];  #wchis is defined in config.py
 my $default_sche      = 60;         #triggers after 120 sec., 

 my $session = Infoblox::Session->new( master   => $host_ip, username => "admin", password => "infoblox" );

#check restore_directory (currently checking in local machine as backup & restore machine done locally)
 if (-d $restore_directory) {
  print "Restore directory is exists\n";
 }
 else {
  print "Look's like reporting restore directory is not exists\n";
  exit(1);
 }


 my $bkup = Infoblox::Grid::ScheduledBackup->new(
   'restore_host' => $restore_host,
   'source' => 'REPORTING',
   'restore_directory' => $restore_directory,
   'restore_username' => $scp_user,
   'operation' => 'RESTORE',
   'restore_type' => "SCP",
   'restore_password' => $scp_passwd, 
   'execute' => 'TRIGGER'
  );

 my @result_array = $session->get( object => "Infoblox::Grid::Reporting");
 my $sche_obj = $result_array[0];
    $sche_obj->scheduled_backup($bkup);
    $session->modify($sche_obj)
        or die("Update Grid Reporting Properties for Restore operaiton has failed: ",
                $session->status_code(). ":" .$session->status_detail());
    print "Update Reporting Properties for Restore operation as sucessfull.\n";

sleep($default_sche + 120);

#wait till bacup gets complted. 
 my $status="NONE";
 my $start_time = `date +%s`;
 my $start = time;
 while ( $status ne 'FINISHED')
 {
    my @result_array = $session->get( object => "Infoblox::Grid::Reporting");  
    $status=$result_array[0]->scheduled_backup->status;
    print "Restore Status : $status \n";
    print "I am waiting for Restore Completion...\n";
    sleep(60);
    my $current_time = `date +%s`;
    if (( int($current_time)  - int($start_time) ) > 1800 )
    {
      print "Looks like Reporting Restore is not completed even after 30 min\n";
      last;
    }
    elsif ( $status eq 'FAILED')
    {
      print "Reporitng Restore failed. Please check the Grid for more informaion\n";
      last;
    }

 }
 if ($status eq 'FINISHED')
 {
   print "Restore operaion is completed successfully\n";
   exit(0);
 }

use strict;
use Infoblox;
use Data::Dumper;
use POSIX qw(strftime);
 my $host_ip        = $ARGV[0];
 my $gm_epoc        = $ARGV[1];  #epoc time of Grid master
 my $bkup_server    = $ARGV[2];  #which is defined in config.py
 my $scp_user       = $ARGV[3];  #which is defined in config.py
 my $scp_passwd     = $ARGV[4];  #which is defined in config.py
 my $bkup_path      = $ARGV[5];  #wchis is defined in config.py
 my $default_sche = 120;         #triggers after 120 sec., 
 my $session = Infoblox::Session->new( master   => $host_ip, username => "admin", password => "infoblox" );

#clearing directory if already exists.  Note: Recomandation backup path should be /tmp directory . 
#Need's to execute following command for 'remote backup server' (currently local machine is considered as bakup server) 
 if (-d $bkup_path) {
     system("rm -rf $bkup_path");
 }
 system ("mkdir $bkup_path");


#date & time
 print "current grid time" . $gm_epoc . ".\n";
 my $new_epoc  = int($gm_epoc) + $default_sche;              #Scheduling backup after 2 min
 print "time when it triggers scheduled backup" . $new_epoc . ".\n";
 my $hour   = strftime "%H",gmtime($new_epoc);  #Featching hour in 24 hour format
 print "hour time" . $hour . ".\n";
 my $minute = strftime "%M",gmtime($new_epoc);  #minute 
 print "minute time" . $minute . ".\n";


 my $bkup = Infoblox::Grid::ScheduledBackup->new(
   'backup_server' => $bkup_server,
   'source' => 'REPORTING',
   'backup_frequency' => 'Daily',
   'hour_of_day' => $hour,
   'minute_of_hour' => $minute,
   'path' => $bkup_path,
   'user' => $scp_user,
   'operation' => 'BACKUP',
   'backup_type' => "SCP",
   'password' => $scp_passwd, 
   'disabled' =>'false'
  );

 my @result_array = $session->get( object => "Infoblox::Grid::Reporting");
 my $sche_obj = $result_array[0];
    print Dumper "Scheduled object" . $sche_obj . ".\n";
    $sche_obj->scheduled_backup($bkup);
    $session->modify($result_array[0])
        or die("Update Grid Reporting Properties for Scheduled Backup has failed: ",
                $session->status_code(). ":" .$session->status_detail());
    print "Update Reporting Properties for Schedule Backup as sucessfull.\n";


sleep(120);

#wait till bacup gets complted. 
 my $status="NONE";
 my $start_time = `date +%s`;
 print "START TIME" . $start_time . ".\n";
 my $start = time;
 print "START" . $start . ".\n";
 while ( $status ne 'FINISHED')
 {
    my @result_array = $session->get( object => "Infoblox::Grid::Reporting");  
    $status=$result_array[0]->scheduled_backup->status;
    print "Backup Status : $status \n";
    print "I am waiting for Backup Completion...\n";
    sleep(60);
    my $current_time = `date +%s`;
    if (( int($current_time)  - int($start_time) ) > 1800 )
    {
      print "Looks like Reporting backup is not completed even after 30 min\n";
      last;
    }
    elsif ( $status eq 'FAILED')
    {
      print "Reporitng Backup is failed. Please check the Grid for more informaion\n";
      last;
    }

 }
 if ($status eq 'FINISHED')
 {
   print "Backup operaion is completed successfully\n";
   #exit(0);
 }


 my $bkup = Infoblox::Grid::ScheduledBackup->new(
   'disabled' =>'true'
  );


 my @result_array = $session->get( object => "Infoblox::Grid::Reporting");
 my $sche_obj = $result_array[0];
    print Dumper "Scheduled object" . $sche_obj . ".\n";
    $sche_obj->scheduled_backup($bkup);
    $session->modify($result_array[0])
        or die("Update Grid Reporting Properties for Scheduled Backup has failed: ",
                $session->status_code(). ":" .$session->status_detail());
    print "Update Reporting Properties for Schedule Backup as sucessfull.\n";


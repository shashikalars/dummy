#!/usr/bin/perl
########################################################################
#                                                                      #
# Copyright (c) Infoblox Inc., 2013                                    #
#                                                                      #
########################################################################
#
# File: simulation_perf.pl
#
# Description:
#   Script to measure the radius simulation operations
#
# Author: Nagarajaiah H M
#
# History:
#    02/03/2016 (Nagarajaiah H M) - Created
#
#######################################################################

use Time::HiRes qw(gettimeofday tv_interval);
use Data::Dumper;

$file_path = $ARGV[0];
$cisco_server_1 = $ARGV[1];;
chomp($file_path);
chomp($cisco_server_1);

my $start_time;
my $end_time;
my @array = ("qa000001".."qa001000");
my $num_users =1000;


my $filename = $file_path;
open( my $fh => $filename) || die "Cannot open $filename: $!";
foreach my $user (@array)
{
        while(my $line = <$fh>)
        {
            my @row = split("\t",$line);
            print $user . "---" . $row[$ip] . "\n";
            $address=$row[$ip];
            chomp($address);
            $start_time =  [gettimeofday];
	    print Dumper $start_time;
	    print "is the start time\n";
            sleep 1;
            #print $user . "---" . $row[$ip] . "\n";
            #system("cd /home/mreddy/Cisco-ISE/Radius;java -cp RadiusSimulator.jar -DUSERNAME=$user -DPASSWORD=Infoblox1492 -DRADIUS_SECRET=secret -DFRAMED_IP_ADDRESS=$address -DCALLING_STATION_ID=11:11:11:11:12:13 -DAUDIT_SESSION_ID=1002 -DFRAMED_IP_MASK=255.255.255.0 RadiusAccountingStart $cisco_server_1");
            #system("cd /home/mreddy/Cisco-ISE/Radius;java -cp RadiusSimulator.jar -DUSERNAME=$user -DPASSWORD=Infoblox1492 -DRADIUS_SECRET=secret -DFRAMED_IP_ADDRESS=$address -DCALLING_STATION_ID=11:11:11:11:12:13 -DAUDIT_SESSION_ID=1002 -DFRAMED_IP_MASK=255.255.255.0 RadiusAuthentication $cisco_server_1");
            $end_time = [gettimeofday];
            print Dumper $end_time;
            print "is the end time\n";
            last;
        }
        my $time_elapsed = tv_interval $start_time, $end_time;
	print $time_elapsed;
	printf("$action $object_type for $username: %.4f\n", $time_elapsed );
	print $time_elapsed;
	print "\n";
	$total_time = $total_time + $time_elapsed;
	$total_time = sprintf("%.4f", $total_time);
	print $total_time . "\n";

}
close($fh);
#system("cd /home/mreddy/Cisco-ISE/Radius;java -cp RadiusSimulator.jar -DUSERNAME=qa00$a$b$c$d -DPASSWORD=Infoblox1492 -DRADIUS_SECRET=secret -DFRAMED_IP_ADDRESS=10.0.0.$i -DCALLING_STATION_ID=11:11:11:11:$a$b:$c$d -DAUDIT_SESSION_ID=$a$b$c$d -DFRAMED_IP_MASK=255.255.255.0 RadiusAccountingStart $cisco_server_1");
#system("cd /home/mreddy/Cisco-ISE/Radius;java -cp RadiusSimulator.jar -DUSERNAME=qa00$a$b$c$d -DPASSWORD=Infoblox1492 -DRADIUS_SECRET=secret -DFRAMED_IP_ADDRESS=10.0.0.$i -DCALLING_STATION_ID=11:11:11:11:$a$b:$c$d -DAUDIT_SESSION_ID=$a$b$c$d -DFRAMED_IP_MASK=255.255.255.0 RadiusAuthentication $cisco_server_1");
        
#my $time_elapsed = tv_interval $start_time, $end_time;
#printf("$action $object_type for $username: %.4f\n", $time_elapsed );
#print $time_elapsed;
#print "\n";
#$total_time = $total_time + $time_elapsed;
#$total_time = sprintf("%.4f", $total_time);
#print $total_time . "\n";

my $avg_time = $total_time / $num_users;
$avg_time = sprintf("%.4f",$avg_time);
print"***********************************************************************************\n";
print" Total time taken for Creating the network users = $total_time Seconds \n";
print" Average time taken for Creating the single network user = $avg_time Seconds. \n";
print"***********************************************************************************\n";

print "$total_time\n";



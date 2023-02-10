#! /usr/bin/perl
########################################################################
#                                                                      #
# Copyright (c) Infoblox Inc., 2006                                    #
#                                                                      #
########################################################################
#
# File: snmp_trap.pl
#
# Description:
#    To get the snmptrap info 
#
# Input Options:
#    -i <server IP> required while downloading mibs directory
#    -t <operation> [mibs|start|stop|kill] 
#		'mibs' to download mibs directory from appliance 
#		'start' to start the snmptrapd demon process 
#		'kill' to kill the named process in appliance to send trap message
#		'stop' to stop the demon process 
#    -e <expected result> eg. [positive|negative]
#    -w <notes> add notes for this specify test.
#
# Output:
#    0: Test success
#    1: Test failed
#
# Author: Prasanta Narah 
# Usage:
#     snmp_trap.pl -i <server IP> -t <mibs|kill> -e <expected result> to download mibs/kill named process from appliance
#     snmp_trap.pl -t <start|stop> -e <expected result> to start and stop the snmptrapd
#
# History:
#    10/07/06 (Prasanta Narah) - Created
########################################################################
use strict;
use Getopt::Std;

use FindBin qw($Bin);
use lib "$Bin";
use Common_func;


my $pathToThis=`dirname $0`;
chomp($pathToThis);


my %option = ();
getopt("itew",\%option);

if(!defined($option{t}))
{ &co_printErrorMessage("Operation Error","-t <operation> not defined");exit(1);}
if(!defined($option{e}))
{ &co_printErrorMessage("Expected result Warning","-e <expected result> not defined, assume POSITIVE result");}


my $server_ip = $option{i};
my $operation = $option{t};
my $flag = $option{e};

my $err_count = 0;
my $MessageText;

if(defined($option{w}))
{
	my $msg = $option{w};
	system("ibwrite -m $msg -t 20");
}

if( !defined($flag) || (length($flag) <= 0) )
{
  $flag = "positive";
}

if( (lc($flag) ne "positive") && (lc($flag) ne "negative") )
{
  &co_printErrorMessage("Flag Error","Expected result not recongized, please use either \"positive\" or \"negative\"");
  exit(1);
}

if ((lc($operation) ne "start") && (lc($operation) ne "stop") && (lc($operation) ne "kill") && (lc($operation) ne "mibs"))
{
  &co_printErrorMessage("Operation Type Error","Operation type not recognized, please use either \"start\", \"stop\",\"kill\" or \"mibs\"");
  exit(1);
}



my $dumpDir = "./dump";
my $snmptrapd = "snmptrapd";

system ("mkdir -p $dumpDir");
my $mibsdir="$dumpDir/mibs";
my $simmib = "$mibsdir/IB-SMI-MIB.txt";
my $trapmib = "$mibsdir/IB-TRAP-MIB.txt";


if($operation  eq "start")   ## Start the snmptrapd process 
{

my $grepOutput =  `grep -c \'disableAuthorization\' /etc/snmp/snmptrapd.conf`;
if ( $grepOutput == 0 ) {	
  print "Starting with snmp release 5.3, access control checks will be applied to incoming notifications. Hence disabling authorization\n";
  system("echo \"disableAuthorization yes\" >> /etc/snmp/snmptrapd.conf");
}

system("rm -rf $dumpDir/snmptrapd.pid $dumpDir/snmptrapd.log");
system("touch $dumpDir/snmptrapd.pid $dumpDir/snmptrapd.log; chmod 666 $dumpDir/snmptrapd.pid $dumpDir/snmptrapd.log");

 #Check if the snmptrapd demon process is running
 system("ps -ef |grep -v grep |grep $snmptrapd");
 my $GrepOut = $?;
 if ($GrepOut == 0)
  {
      &co_printErrorMessage("Process Error", "snmptrapd process already running.");
      $err_count++;
  }
  else
    {#start the snmptrap demon.
	system("sudo snmptrapd -m $simmib:$trapmib -d  -p $dumpDir/snmptrapd.pid -Lf $dumpDir/snmptrapd.log -F \"%v %w %W\n\" &");
	my $trapdOut = $?;
	if($trapdOut != 0)
  	{
	$MessageText = "Not able to start snmptrapd";
  	}else{
		$MessageText = "Started snmptrapd and putting the log to ./dump/snmptrapd.log file.";
	    }
	my $result = !$trapdOut;
	$err_count += &co_printOperation("snmp_trap.pl", "start snmptrapd process", $flag, $result, $MessageText, "DEFAULT");

    }

}
elsif ($operation eq "stop")                    ## Stop the snmptrapd demon and get the trap info
{
 #Check if the snmptrapd demon process is running
 system("ps -ef |grep -v grep |grep $snmptrapd");
 my $grepOut = $?;
 if ($grepOut != 0){
      &co_printErrorMessage("Process Error", "snmptrapd process not running.");
      $err_count++;
   }
  else{
 	my $killout = system("cat $dumpDir/snmptrapd.pid |xargs sudo kill -9");
 	my $killOut = $?;
 	if($killOut != 0)
   	{
		$MessageText = "Not able to kill the snmptrapd process.";
   	}else{
		$MessageText = "Sucessfully killed the snmptrapd process.";
	     }
        my $result = !$killOut;
        $err_count += &co_printOperation("snmp_trap.pl", "stop snmptrapd process", $flag, $result, $MessageText, "DEFAULT");

        print"\n+++++++++++++++++++++++++++++++:Start of SNMP Trap log:++++++++++++++++++++++++++++++++++\n";
        if(open(MYFILE,"$dumpDir/snmptrapd.log"))
        {
           my @f_content = <MYFILE>;
	   print @f_content;
        }else{
		&co_printErrorMessage("File Error", "Can't open $dumpDir/snmptrapd.log file.");
  	    	$err_count++;
		}
        print"\n+++++++++++++++++++++++++++++++:End of SNMP Trap log:++++++++++++++++++++++++++++++++++++\n";
    }

}
elsif($operation eq "kill")
{
      my $localProcesskill = "$pathToThis/killnamed.sh";
      my $remoteProcesskill = "/tmp/killnamed.sh";
      my $localKillStarter = "$pathToThis/killnamedStarter.sh";

      my $sshOutput =  system ("ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root\@$server_ip /bin/true");
      my $sshResult = $?;
      if ($sshResult != 0)
      {
        &co_printErrorMessage("SSH Error", "Unable to SSH to server:$server_ip");
        $err_count++;
      }
      else
      {
	 #upload the killnamed.sh 
	 $sshOutput = system("scp -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null 2>/dev/null $localProcesskill root\@$server_ip:$remoteProcesskill");
   	$sshResult = $?;
	if ($sshResult == 0)
   	{
      		print "Uploaded script $localProcesskill to $remoteProcesskill on $server_ip\n";
   	}
	else
   	   {
        	print "Unable to upload script $localProcesskill to $remoteProcesskill on $server_ip.\n";
      		$err_count++;
   	   }	

   	# start script killnamed.sh,
   	my $killOutput =  system("ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null 2>/dev/null root\@$server_ip /tmp/killnamed.sh");
   	my $killResult = $?;
   	if ($killResult != 0)
   	{
      		$MessageText = "unable to start $remoteProcesskill on $server_ip.";
   	}
	else{
		$MessageText = "Sucessfully killed named process on $server_ip.";
	}
	my $result = !$killResult;
        $err_count += &co_printOperation("snmp_trap.pl", "kill named process", $flag, $result, $MessageText, "DEFAULT");

      }
		
}
elsif($operation eq "mibs")
  {
      my $serverMibsDirName = "/usr/share/snmp/mibs";
      my $sshOutput =  system ("ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root\@$server_ip /bin/true");
      my $sshResult = $?;
      if ($sshResult != 0)
      {
        &co_printErrorMessage("SSH Error", "Unable to SSH to server:$server_ip");
        $err_count++;
      }
      else
      {
        if (-e $mibsdir) {system ("rm -rf $mibsdir");}
        # download the given dir from the server to the local /dump direcotry
        $sshOutput = system("scp -pr -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root\@$server_ip:$serverMibsDirName $dumpDir");
        $sshResult = ! $?;
        $MessageText = "Operation for mibs directory download.";
        $err_count += &co_printOperation("snmp_trap.pl", "download mibs from server", $flag, $sshResult, $MessageText, "DEFAULT");
      }

}


my $lFinalCode = 1; # Default is fail
if($err_count == 0)
{
	$lFinalCode = 0;
}


exit &co_printSummary($lFinalCode);



#!usr/bin/perl
use Time::Piece;
use Data::Dumper;

our ($pass_cases,$failed_cases,$total_cases,$skipped_cases)=0;
my ($start_time, $end_time, $test_start_timestamp, $test_end_timestamp);
my ($session, $mgmt_ip, $desc, $temp_id, $description);
my $execution_time;
my %output_summary;
my $myname="$0";
$myname=~s/.*\///;
#my %tc_to_sid_map = ( 1 => "110000100", 2 => "110000200", 3 => "110000300", 4 => "130000700", 5 => "130000700", 6 => "130000700", 7 => "130000800", 8 => "130000800", 9 => "130000800", 10 => "130000800", 11 => "110100100", 12 => "110100200", 13 => "110100300", 14 => "110100400", 15 => "110100500", 16 => "110100600", 17 => "110100600", 18 => "110100600", 19 => "110100600", 20 => "110100700", 21 => "110100700", 22 => "110100700", 23 => "110100800", 24 => "110100900", 25 => "110100900", 26 => "110100900", 27 => "110100900", 28 => "110100900", 29 => "130100500", 30 => "130100500", 31 => "110100850", 32 => "110100850", 33 => "200000001", 34 => "200000002", 35 => "200000003", 36 => "200000004", 37 => "130300300", 38 => "130300400", 39 => "130100600", 40 => "130100600", 41 => "130100600", 42 => "130000700", 43 => "130000700", 44 => "130400200", 45 => "130200100", 46 => "130200200", 47 => "130200300", 48 => "130200400", 49 => "130500100", 50 => "130500200", 51 => "130500300", 52 => "130500400", 53 => "130500500", 54 => "130500600", 55 => "130500700", 56 => "130500800", 57 => "130500900", 58 => "130501000", 59 => "130501100", 60 => "130501200", 61 => "130501300", 62 => "130501400", 63 => "130501500", 64 => "130501600", 65 => "130501700", 66 => "130501800", 67 => "130501900", 68 => "130502000", 69 => "130502100", 70 => "130502200", 71 => "130502300", 72 => "130502400", 73 => "130502500", 74 => "130502600", 75 => "130502700", 76 => "130502800", 77 => "130502900", 78 => "130503000", 79 => "130503100", 80 => "130503200", 81 => "130503300", 82 => "130503400", 83 => "130503500", 84 => "130503600", 85 => "130503700", 86 => "130503800", 87 => "130503900", 88 => "130504000", 89 => "130504100", 90 => "130504200", 91 => "130504300", 92 => "130504400", 93 => "130504500", 94 => "130504600", 95 => "130504700", 96 => "130504800", 97 => "130504900", 98 => "130505000", 99 => "130505100", 100 => "130505200", 101 => "130505300", 102 => "130505400", 103 => "130505500", 104 => "130505600", 105 => "130700100", 106 => "130800100", 107 => "130700200", 108 => "130700200", 109 => "130700200", 110 => "130700200", 111 => "130700400", 112 => "130700500", 113 => "130700500", 114 => "130700500", 115 => "130700500", 116 => "130700500", 117 => "130700500", 118 => "120600047", 119 => "130900300", 120 => "120600550", 121 => "120600550", 122 => "140000100", 123 => "140000200", 124 => "140000500", 125 => "140000600", 126 => "140000700", 127 => "140000800" );
#my %tc_to_sid_map = ( 1 => "110000100", 2 => "110000200", 3 => "110000300", 4 => "130000700", 5 => "130000700", 6 => "130000700", 7 => "130000800", 8 => "130000800", 9 => "130000800", 10 => "130000800", 11 => "110100100", 12 => "110100200", 13 => "110100300", 14 => "110100400", 15 => "110100500", 16 => "110100600", 17 => "110100600", 18 => "110100600", 19 => "110100600", 20 => "110100700", 21 => "110100700", 22 => "110100700", 23 => "110100800", 24 => "110100900", 25 => "110100900", 26 => "110100900", 27 => "110100900", 28 => "110100900", 29 => "130100500", 30 => "130100500", 31 => "110100850", 32 => "110100850", 33 => "200000001", 34 => "200000002", 35 => "200000003", 36 => "200000004", 37 => "130300300", 38 => "130300400", 39 => "130100600", 40 => "130100600", 41 => "130100600", 42 => "130000700", 43 => "130000700", 44 => "130400200", 45 => "130200100", 46 => "130200200", 47 => "130200300", 48 => "130200400", 49 => "130500100", 50 => "130500200", 51 => "130500300", 52 => "130500400", 53 => "130500500", 54 => "130500600", 55 => "130500700", 56 => "130500800", 57 => "130500900", 58 => "130501000", 59 => "130501100", 60 => "130501200", 61 => "130501300", 62 => "130501400", 63 => "130501500", 64 => "130501600", 65 => "130501700", 66 => "130501800", 67 => "130501900", 68 => "130502000", 69 => "130502100", 70 => "130502200", 71 => "130502300", 72 => "130502400", 73 => "130502500", 74 => "130502600", 75 => "130502700", 76 => "130502800", 77 => "130502900", 78 => "130503000", 79 => "130503100", 80 => "130503200", 81 => "130503300", 82 => "130503400", 83 => "130503500", 84 => "130503600", 85 => "130503700", 86 => "130503800", 87 => "130503900", 88 => "130504000", 89 => "130504100", 90 => "130504200", 91 => "130504300", 92 => "130504400", 93 => "130504500", 94 => "130504600", 95 => "130504700", 96 => "130504800", 97 => "130504900", 98 => "130505000", 99 => "130505100", 100 => "130505200", 101 => "130505300", 102 => "130505400", 103 => "130505500", 104 => "130505600", 105 => "130700100", 106 => "130800100", 107 => "130700200", 108 => "130700200", 109 => "130700200", 110 => "130700200", 111 => "130700400", 112 => "130700500", 113 => "130700500", 114 => "130700500", 115 => "130700500", 116 => "130700500", 117 => "130700500", 118 => "130900300", 119 => "140000100", 120 => "140000200", 121 => "140000500", 122 => "140000600", 123 => "140000700", 124 => "140000800" );

my %tc_to_sid_map = ( 1 => "110000100", 2 => "110000200", 3 => "110000300", 4 => "130000700", 5 => "130000700", 6 => "130000700", 7 => "130000800", 8 => "130000800", 9 => "130000800", 10 => "130000800", 11 => "110100100", 12 => "110100200", 13 => "110100300", 14 => "110100400", 15 => "110100500", 16 => "110100600", 17 => "110100600", 18 => "110100600", 19 => "110100600", 20 => "110100700", 21 => "110100700", 22 => "110100700", 23 => "110100800", 24 => "110100900", 25 => "110100900", 26 => "110100900", 27 => "110100900", 28 => "110100900", 29 => "130100500", 30 => "130100500", 31 => "110100850", 32 => "110100850", 33 => "200000001", 34 => "200000002", 35 => "200000003", 36 => "200000004", 37 => "130300300", 38 => "130300400", 39 => "130100600", 40 => "130100600", 41 => "130100600", 42 => "130000700", 43 => "130000700", 45 => "130200100", 46 => "130200200", 47 => "130200300", 48 => "130200400", 49 => "130500100", 50 => "130500200", 51 => "130500300", 52 => "130500400", 53 => "130500500", 54 => "130500600", 55 => "130500700", 56 => "130500800", 57 => "130500900", 58 => "130501000", 59 => "130501100", 60 => "130501200", 61 => "130501300", 62 => "130501400", 63 => "130501500", 64 => "130501600", 65 => "130501700", 66 => "130501800", 67 => "130501900", 68 => "130502000", 69 => "130502100", 70 => "130502200", 71 => "130502300", 72 => "130502400", 73 => "130502500", 74 => "130502600", 75 => "130502700", 76 => "130502800", 77 => "130502900", 78 => "130503000", 79 => "130503100", 80 => "130503200", 81 => "130503300", 82 => "130503400", 83 => "130503500", 84 => "130503600", 85 => "130503700", 86 => "130503800", 87 => "130503900", 88 => "130504000", 89 => "130504100", 90 => "130504200", 91 => "130504300", 92 => "130504400", 93 => "130504500", 94 => "130504600", 95 => "130504700", 96 => "130504800", 97 => "130504900", 98 => "130505000", 99 => "130505100", 100 => "130505200", 101 => "130505300", 102 => "130505400", 103 => "130505500", 104 => "130505600", 105 => "130700100", 107 => "130700200", 108 => "130700200", 109 => "130700200", 110 => "130700200", 111 => "130700400", 112 => "130700500", 113 => "130700500", 114 => "130700500", 115 => "130700500", 116 => "130700500", 117 => "130700500", 118 => "130900300", 119 => "140000100", 120 => "140000200", 121 => "140000500", 122 => "140000600", 123 => "140000700", 124 => "140000800" );

my $PAPI_directory="/tmp/$myname.$$";

# Read the output log into an array

  open(LF,"<output.txt") or die "Cannot open output.txt file for read :$!";
  our @output_log = <LF>;
  close(LF);

get_testcase_cases_count_n_start_end_timestamps();

#############################################################################################
## Get test cases total count, pass/fail/skip count and the start and end timestamps        #
#############################################################################################
sub get_testcase_cases_count_n_start_end_timestamps
{
  foreach (@output_log)
  {
    if($_ =~ m/\s+(\d+) Test Case.*?Passed/) {
      $pass_cases += $1;
      print "\n Total passed test cases count is: $pass_cases \n";
    }elsif($_ =~ m/\s+(\d+) Test Case.*?Failed/) {
      $failed_cases += $1;
      print "\n Total failed test cases count is: $failed_cases \n";
    }elsif($_ =~ m/\s+(\d+) Test Case.*?Skipped/) {
      $skipped_cases += $1;
      print "\n Total skipped test cases count is: $skipped_cases \n";
    }elsif($_ =~ m/Program = .*?at\s+(\w+\s+\w+\s+\d+\s+(\d\d:\d\d:\d\d)\s+\d+)/) {
      $start_time=$2;
      print "\n Start time is : $start_time \n";
      $test_start_timestamp=$1;
      print "\n Test Start timestamp is : $test_start_timestamp \n";
    }elsif($_ =~ m/End of.*?at\s+(\w+\s\w+\s+\d+\s+(\d\d:\d\d:\d\d)\s+\d+)/) {
      $end_time=$2;
      print "\n End time is : $end_time \n";
      $test_end_timestamp=$1;
      print "\n Test End timestamp is : $test_end_timestamp \n";
    }elsif ($_ =~ m/SSH IP Address = (.*)/) {
      chomp($1);
      $mgmt_ip=$1;
      print "\n Mgmt IP is $mgmt_ip \n";
    }
  }
}
get_each_test_case_status();

#############################################################################################
## Get each test case details, like rule id, pass/fail/skip status, output                  #
#############################################################################################
sub get_each_test_case_status
{
  my $array_index=0;
  my @result_log;
  foreach(@output_log)
  {
    chomp($_);
    $array_index++;
    @result_log="";
    my @output_log_report="";
    if($_ =~ m/Sending Test Case (\d+) of \d+(.*)/) {
      print "Tc id is $1\n";
      $output_summary{$1}{command} = $2;
      my $rule_sid= $tc_to_sid_map{$1};
      $output_summary{$1}{rule_sid} = $rule_sid;
      $desc = get_rule_description($output_summary{$1}{rule_sid});
      $output_summary{$1}{tc_name} = "SID: $output_summary{$1}{rule_sid} - $desc - Test Case # $1";
    } elsif($_ =~ m/Skipping Test Case (\d+) (.*)/) {
      print "Tc id is $1\n";
      $output_summary{$1}{command} = $2;
      my $rule_sid= $tc_to_sid_map{$1};
      $output_summary{$1}{rule_sid} = $rule_sid;
      $desc = get_rule_description($output_summary{$1}{rule_sid});
      $output_summary{$1}{tc_name} = "SID: $output_summary{$1}{rule_sid} - $desc -  $2 - Test Case # $1";
    } elsif($_ =~ m/(\w+)\sTest Case # (\d+) - (Rule (\d+) - .*)/) {
      $output_summary{$2}{status} = $1;
print "summary of $2 is $output_summary{$2}{status}\n";
      push(@result_log,$3);
      $i=$array_index + 1;
      until($output_log[$i] !~ /^\s/)
      {
        last if($output_log[$i] =~ m/\s+\d/);
        push(@result_log,$output_log[$i]);
        $i++;
      }
      $output_summary{$2}{result} = [@result_log];
      my $tc_id=$2;
      if($1 eq "FAIL") {
        if($_ =~ m/.*?See\s(.*)/) {
          my $output_file=$1;
          open(OF,"<$output_file") or die "Cannot open $output_file file for read :$!";
          @output_log_report = <OF>;
#New change
          my @array_indexs_with_quotes=grep $output_log_report[$_] =~ /\"/, 0..$#output_log_report;
          foreach (@array_indexs_with_quotes)
          {
           $output_log_report[$_] =~ s/\"//g;
          }

          my @array_indexs_with_semicolon=grep $output_log_report[$_] =~ /^\;/, 0..$#output_log_report;
          foreach (@array_indexs_with_semicolon)
          {
           $output_log_report[$_] =~ s/\;//g;
          }

          my @array_indexs_with_special_char=grep $output_log_report[$_] =~ /\<\<\>\>/, 0..$#output_log_report;
          foreach (@array_indexs_with_special_char)
          {
           $output_log_report[$_] =~ s/\<\<\>\>//g;
          }
# Change ends here
          $output_summary{$tc_id}{output_log}= [@output_log_report];
          $output_summary{$tc_id}{error_log} = $output_summary{$tc_id}{result};
          close(OF);
        }
      }
      if($_ =~ m/\w+\s\w+\s\d+\s(\d\d:\d\d:\d\d)\s.*?Sending Test Case (\d+) of (\d+)/) {
        $output_summary{$2}{start_time} = $1;
      }
    }elsif ($_ =~ m/^(\w+)\sTest Case # (\d+) - ((\d+) .*)/) {
        $output_summary{$2}{status} = $1;
print "summary of $2 is $output_summary{$2}{status}\n";
        $output_summary{$2}{result} = [$3];
    }elsif ($_ =~ m/^(\w+)\sTest Case # (\d+) - (Found.*?(\d+).*)/) {
        $output_summary{$2}{status} = $1;
print "summary of $2 is $output_summary{$2}{status}\n";
        $output_summary{$2}{result} = [$3];
        if($1 eq "FAIL") {
          $output_summary{$2}{error_log} = [$3];
        }
    }elsif ($_ =~ m/^(\w+)\sTest Case # (\d+) - (Expected.*)/) {
        $output_summary{$2}{status} = $1;
print "summary of $2 is $output_summary{$2}{status}\n";
        $output_summary{$2}{result} = [$3];
        if($1 eq "FAIL") {
          $output_summary{$2}{error_log} = [$3];
        }
    }elsif ($_ =~ m/^(\w+)\sTest Case # (\d+) - Failed.*?See\s(.*)/) {
        $output_summary{$2}{status} = $1;
print "summary of $2 is $output_summary{$2}{status}\n";
        $output_summary{$2}{result} = [$3];
        my $tc_id=$2;
        if($1 eq "FAIL") {
          my $output_file=$3;
          open(OF,"<$output_file") or die "Cannot open $output_file file for read :$!";
          @output_log_report = <OF>;
#New change
          my @array_indexs_with_quotes=grep $output_log_report[$_] =~ /\"/, 0..$#output_log_report;
          foreach (@array_indexs_with_quotes)
          {
           $output_log_report[$_] =~ s/\"//g;
          }

          my @array_indexs_with_semicolon=grep $output_log_report[$_] =~ /^\;/, 0..$#output_log_report;
          foreach (@array_indexs_with_semicolon)
          {
           $output_log_report[$_] =~ s/\;//g;
          }

          my @array_indexs_with_special_char=grep $output_log_report[$_] =~ /\<\<\>\>/, 0..$#output_log_report;
          foreach (@array_indexs_with_special_char)
          {
           $output_log_report[$_] =~ s/\<\<\>\>//g;

          }
# Change ends here

          $output_summary{$tc_id}{output_log}= [@output_log_report];
          $output_summary{$tc_id}{error_log} = $output_summary{$tc_id}{result};
          close(OF);
        }
    }
  }
}
#############################################################################################
## Get the time difference                                                                  #
#############################################################################################
sub get_time_diff
{
  my $fmt="%H:%M:%S";
  my $test_end_time=shift;
  my $test_start_time=shift;
  my $time_diff = Time::Piece->strptime("$test_end_time",$fmt) - Time::Piece->strptime("$test_start_time",$fmt);
  return $time_diff;
}

$total_cases = $pass_cases + $failed_cases + $skipped_cases;
$execution_time = get_time_diff($end_time,$start_time);
print "\n Total test cases = $total_cases \n";
print "\n Total execution time = $execution_time \n";
generate_report();


#############################################################################################
## Generate JUNIT XML report                                                                #
#############################################################################################
sub generate_report
{
#Write JUnit Report xml file
  open(FH,">JUnitReport.xml") or die "Cannot open JunitReport.xml file for write :$!";
  select FH;
print qq(<?xml version="1.0" encoding="UTF-8"?>\n);
print qq(<testsuites>\n);
  print qq(\t<testsuite classname="REA_BAT" disabled="0" errors="0" failures="$failed_cases" hostname="$hostname" id="1" name="ADP REA BAT Rules" package="" skipped="$skipped_cases" tests="$total_cases" time="$execution_time" timestamp="$test_start_timestamp">\n);
  foreach (1..$total_cases)
  {
    print qq(\t\t<testcase id="$_" classname="REA_BAT.PASS" name="$output_summary{$_}{tc_name}" status="$output_summary{$_}{status}" time="">\n) if($output_summary{$_}{status} =~ m/PASS/);
    #print qq(\t\t</testcase>\n);
    print qq(\t\t<testcase id="$_" classname="REA_BAT.FAIL" name="$output_summary{$_}{tc_name}" status="$output_summary{$_}{status}" time="">\n) if($output_summary{$_}{status} =~ m/FAIL/);
    #print qq(\t\t</testcase>\n);
    print qq(\t\t<testcase id="$_" classname="REA_BAT.SKIP" name="$output_summary{$_}{tc_name}" status="$output_summary{$_}{status}" time="">\n) if($output_summary{$_}{status} =~ m/SKIP/);
    #print qq(\t\t\t<system-out>\n);
    #print qq(Command $output_summary{$_}{command}}\n);
    #print qq(Output: @{$output_summary{$_}{result}}\n);
    #print qq(Captured_log_content: @{$output_summary{$_}{output_log}}\n) if($output_summary{$_}{status} eq "FAIL");
    #print qq(</system-out>\n);
    #print qq(<failure message="@{$output_summary{$_}{error_log}}"/>\n) if($output_summary{$_}{status} eq "FAIL");
    #print qq(\t\t</testcase>\n);
    print qq(\t\t</testcase>\n) if($output_summary{$_}{status} =~ m/SKIP/);
    print qq(\t\t</testcase>\n) if($output_summary{$_}{status} =~ m/PASS/);
    print qq(\t\t</testcase>\n) if($output_summary{$_}{status} =~ m/FAIL/);
  }
  print qq(\t</testsuite>\n);
  print qq(</testsuites>\n);
  close(FH);
  select STDOUT;
}

#############################################################################################
## Get rule description                                                                     #
#############################################################################################

sub get_rule_description
{
  my $rule_sid = shift;
  print "Rule id is : $rule_sid \n";
  create_session();
  my $rule = $session->get(object => 'Infoblox::Grid::ThreatProtection::Rule', sid =>$rule_sid);
  my $description = $rule->description();
  my $rule_description=substr($description,0,100);
  return $rule_description;  
}

#############################################################################################
## Create Session                                                                           #
#############################################################################################

sub create_session
{
  get_API_Modules();
  $session = Infoblox::Session->new('master'=>$mgmt_ip, 'username'=>'admin', 'password'=>'infoblox');
  die "Session creation has failed: $!\n" if(!$session); 
}
 
##############################################################################################
## Get the Perl API                                                                          #
##############################################################################################

sub get_API_Modules
{  
  system("/import/tools/qa/tools/bin/getPAPI $mgmt_ip $PAPI_directory >/dev/null");
  unshift(@INC, "$PAPI_directory");                        # Jump through hoops so this program can
  {eval "require Infoblox";die if $@;Infoblox->import();}  # use the just-now uploaded Perl API.
}



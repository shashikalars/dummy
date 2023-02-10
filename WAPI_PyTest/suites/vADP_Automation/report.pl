#!/usr/bin/perl

use strict;
use warnings;
use diagnostics;

my ($size, $str, $i, $inp_file, $out_file, $platform);
my (@content, @suites, @pass, @fail, @total);
my ($name, $pass_count, $fail_count, $skip_count,$uncheck_count, $tot_count);
my ($pass_sum, $fail_sum, $skip_sum, $uncheck_sum, $tot_sum);

$inp_file = shift;
$platform = shift;
die "Given file '$inp_file' either empty or doesn't exist\n" unless (-e $inp_file && -s $inp_file);
if ((defined ($platform)) && ($platform ne "")) {
    $out_file = "/tmp/VADP_Physical_SUMMARY.txt";
} else {
    $out_file = "/tmp/VADP_SUMMARY.txt";
}
open (OUT_DATA, ">$out_file");
$pass_count=$fail_count=$skip_count=$uncheck_count=$tot_count=0;
$pass_sum=$fail_sum=$skip_sum=$uncheck_sum=$tot_sum=0;

@suites = `grep -oP "Executing \\K.*" $inp_file`;
@pass = `grep "Passed" $inp_file`;
@fail = `grep "Failed" $inp_file | grep -v "FAIL Test Case"`;
@total = `grep "Total" $inp_file`;

chomp (@suites, @pass, @fail, @total);
$size = scalar @suites;

print OUT_DATA  "<h3>Overall Summary:<h3>\n";
print OUT_DATA "<table border=1>\n";
print OUT_DATA "<tr><th>Suite Name</th><th>Pass</th>";
print OUT_DATA "<th>Fail</th><th>Skip</th><th>Unchecked</th><th>Total</th></tr>\n";

for ($i=0;$i<$size;$i++) {
    $name = $suites[$i];
    if ($name =~ /REA/) {
      if ($name =~ /LAN V6/i) {
	$str = `grep -iA 350 "REA.*LAN V6.*Automation" $inp_file | grep "Skipped"`;
        $skip_count = $1 if ($str =~ /(\d{1,3})/);
	$str = `grep -iA 350 "REA.*LAN V6.*Automation" $inp_file | grep "Unchecked"`;
	$uncheck_count = $1 if ($str =~ /(\d{1,3})/);
      } else {
	$str = `grep -iA 350 "REA Automation" $inp_file | grep "Skipped"`;
        $skip_count = $1 if ($str =~ /(\d{1,3})/);
	$str = `grep -iA 350 "REA Automation" $inp_file | grep "Unchecked"`;
        $uncheck_count = $1 if ($str =~ /(\d{1,3})/);
      }
    }
    $pass_count = $1 if ($pass[$i] =~ /(\d{1,3})/);
    $fail_count = $1 if ($fail[$i] =~ /(\d{1,3})/);
    $tot_count  = $1 if ($total[$i] =~ /(\d{1,3})/);
    $pass_sum += $pass_count;
    $fail_sum += $fail_count;
    $skip_sum += $skip_count;
    $uncheck_sum += $uncheck_count;
    print OUT_DATA "<tr><td>$name</td><td>$pass_count</td><td>$fail_count</td><td>$skip_count</td><td>$uncheck_count</td><td>$tot_count</td></tr>\n";
    $pass_count=$fail_count=$skip_count=$uncheck_count=$tot_count=0;
}
$tot_sum = $pass_sum + $fail_sum + $skip_sum + $uncheck_sum;
print OUT_DATA "<tr><td><b>Total Cases</b></td><td><b>$pass_sum</b></td><td><b>$fail_sum</b></td><td><b>$skip_sum</b></td><td><b>$uncheck_sum</b></td><td><b>$tot_sum</b></td></tr>\n";
print OUT_DATA "</table><br />\n";
close OUT_DATA;


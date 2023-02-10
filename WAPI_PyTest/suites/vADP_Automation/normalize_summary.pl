#!/usr/bin/perl -w

use strict;
use warnings;
use diagnostics;

my ($size, $str, $i, $inp_file, $out_file);
my (@content, @suites, @pass, @fail, @total);
my ($name, $pass_count, $fail_count, $skip_count, $tot_count);
my ($pass_sum, $fail_sum, $skip_sum, $tot_sum);

$inp_file = shift;
die "Given file '$inp_file' either empty or doesn't exist\n" unless (-e $inp_file && -s $inp_file);

$pass_count=$fail_count=$skip_count=$tot_count=0;
$pass_sum=$fail_sum=$skip_sum=$tot_sum=0;

@suites = `grep -oP "Executing \\K.*" $inp_file`;
@pass = `grep "Passed" $inp_file`;
@fail = `grep "Failed" $inp_file | grep -v "FAIL Test Case"`;
@total = `grep "Total" $inp_file`;

chomp (@suites, @pass, @fail, @total);
$size = scalar @total;

print "\nExecuting $suites[0]\n";

for ($i=0;$i<$size;$i++) {
    $pass_count = $1 if ($pass[$i] =~ /(\d{1,3})/);
    $fail_count = $1 if ($fail[$i] =~ /(\d{1,3})/);
    $tot_count  = $1 if ($total[$i] =~ /(\d{1,3})/);
    $pass_sum += $pass_count;
    $fail_sum += $fail_count;
    $skip_sum += $skip_count;
    $pass_count=$fail_count=$skip_count=$tot_count=0;
}
$tot_sum = $pass_sum + $fail_sum + $skip_sum;
print "\nSummary\n";
print "="x80 . "\n";
print "Total  : $tot_sum\n";
print "Passed : $pass_sum\n";
print "Failed : $fail_sum\n";

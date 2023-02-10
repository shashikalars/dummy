#!/usr/bin/perl -w
# 
# Author : Madhu Kumar
#
# Description: 
# This script downloads the Support bundle for the TP member
# And validates the mandatory files and its size

use strict;
use warnings;
use diagnostics;
use Infoblox;

my $ssh_ip = shift; 
my $tp_ip = shift;

die "Usage: $0 <Grid VIP> <TP Member LAN IP>\n" unless (($ssh_ip =~ /^\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}$/) && ($tp_ip =~ /^\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}$/));

my ($dir, $size, $output, $file, $absolute_path, $pass, $fail);
my (@result, @content_validate);

$dir = "/tmp/sb/";
$file = "${dir}/supportBundle.tar.gz";
@content_validate = (
     #File Names to validate in support bundle
     "infoblox/var/atp_conf/rules.txt",
     "infoblox/var/atp_conf/snort_conf.txt",
     "infoblox/var/atp_conf/sw_atp.yaml",
     "infoblox/var/atp_conf/thresholds.txt",
);

# Creates Session
my $session = Infoblox::Session->new(
     master   => $ssh_ip,
     username => "admin",
     password => "infoblox"
);
die "Session creation failed. Need the appropriate Infoblox Perl Modules.\n" unless (($session->{'statusdetail'}) eq "Operation succeeded");
print "\nExecuting Support Bundle Automation\n\n";

# Clears a tmp directory to download the support bundle
`rm -rf $dir;mkdir -p $dir 2>&1`;

# Download Support Bundle
my @retrieved_objs = $session->export_data(
     type   => "support_bundle",
     path   => "$file",
     member => "$tp_ip" 
);

# Does the downloaded support bundle file exists
die "Failed to download the 'support_bundle'. Re-check the following:\n\tDoes the directory '$dir' have WRITE permission?\n\tIs '$tp_ip' a LAN IP of the TP Member?\n" unless (-e $file);

$output = `file $file`;
die "Downloaded support bundle '$file' is in unexpected format\n.$output\n" unless ($output =~ /compressed data/);
print "SupportBundle download is successful\n\n";

# Un-tar the downloaded support bundle
@result = `tar -xvf $file --directory $dir 2>&1`;
$pass = 0;
$fail = 0;

foreach my $filename (@content_validate) {
     $absolute_path = "${dir}${filename}";
     if (-e "$absolute_path") {
	$size = int (-s "$absolute_path");
	print "The file '$absolute_path'\tsize: $size Bytes\n";
	$pass++;
     } else {
	print "The file '$absolute_path' doesn't exist\n";
	$fail++;
     }  
}

print "\nSummary\n";
print "="x80 . "\n";
print "Total  : " . ($pass+$fail) . "\n";
print "Passed : $pass\n";
print "Failed : $fail\n";


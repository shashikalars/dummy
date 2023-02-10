#!/usr/bin/perl
 use strict;
 use Infoblox;
 my $host = $ARGV[0];
 my $file = $ARGV[1];
 chomp($host);
 chomp($file);
 my $session = Infoblox::Session->new(
     master   => $host,
     username => "admin",
     password => "infoblox",
     timeout => "100000"
 );
 unless ($session) {
    die("Construct session failed: ",
        $session->status_code() . ":" . $session->status_detail());
 }
 print "Session created successfully\n";

 $session->import_data(
     type  => "csv",

     continue_on_error => 'true',
     override => 'override',
     path  => "$file" );

        print $session->status_code() . ":" . $session->status_detail();

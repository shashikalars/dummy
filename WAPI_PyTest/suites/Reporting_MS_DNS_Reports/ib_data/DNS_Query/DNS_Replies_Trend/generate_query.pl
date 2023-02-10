my @zones = ("dns_rt1.com","dns_rt2.com","failure.org");
open(MYOUTFILE, ">input.txt");

foreach $zone (@zones)
{
 for( my $j=1;$j<=24; $j++)
 {
   print MYOUTFILE "arec$j.$zone A \n";
   print MYOUTFILE "nxdomain$j.$zone A \n";
   print MYOUTFILE "arec$j.$zone MX \n";
 }
 for( my $j=1;$j<=24; $j++)
 {
   print MYOUTFILE "aaaa$j.$zone AAAA \n";
 }

 for( my $j=1;$j<=18; $j++)
 {
   print MYOUTFILE "cname$j.$zone CNAME \n";
 }
 for( my $j=1;$j<=18; $j++)
 {
   print MYOUTFILE "mx$j.$zone MX \n";
 }

 for( my $j=1;$j<=18; $j++)
 {
   print MYOUTFILE "txt$j.$zone TXT \n";
 }
 for( my $j=1;$j<=12; $j++)
 {
   print MYOUTFILE "srv$j.$zone SRV \n";
 }
 for( my $j=1;$j<=12; $j++)
 {
   print MYOUTFILE "dname$j.$zone DNAME \n";
 }
 for( my $j=1;$j<=12; $j++)
 {
   print MYOUTFILE "naptr$j.$zone NAPTR \n";
 }

 for( my $j=1;$j<=6; $j++)
 {
   print MYOUTFILE "ptr$j.$zone PTR \n";
 }
}
close(MYOUTFILE);

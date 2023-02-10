my @zones = ("qrqt1.com","qrqt2.com");
open(MYOUTFILE, ">input.txt");

foreach $zone (@zones)
{
 for( my $j=1;$j<=240; $j++)
 {
   print MYOUTFILE "arec$j.$zone A \n";
 }
 for( my $j=1;$j<=240; $j++)
 {
   print MYOUTFILE "aaaa$j.$zone AAAA \n";
 }

 for( my $j=1;$j<=180; $j++)
 {
   print MYOUTFILE "cname$j.$zone CNAME \n";
 }
 for( my $j=1;$j<=180; $j++)
 {
   print MYOUTFILE "mx$j.$zone MX \n";
 }

 for( my $j=1;$j<=180; $j++)
 {
   print MYOUTFILE "txt$j.$zone TXT \n";
 }
 for( my $j=1;$j<=120; $j++)
 {
   print MYOUTFILE "srv$j.$zone SRV \n";
 }
 for( my $j=1;$j<=120; $j++)
 {
   print MYOUTFILE "dname$j.$zone DNAME \n";
 }
 for( my $j=1;$j<=120; $j++)
 {
   print MYOUTFILE "naptr$j.$zone NAPTR \n";
 }

 for( my $j=1;$j<=60; $j++)
 {
   print MYOUTFILE "ptr$j.$zone PTR \n";
 }
}
close(MYOUTFILE);

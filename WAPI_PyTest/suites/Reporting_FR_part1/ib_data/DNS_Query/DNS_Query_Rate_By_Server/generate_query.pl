my @zones = ("member2_1.com","member2_2.com");
open(MYOUTFILE, ">member_2.txt");

foreach $zone (@zones)
{
 for( my $j=1;$j<=200; $j++)
 {
   print MYOUTFILE "arec$j.$zone A \n";
 }
 for( my $j=1;$j<=100; $j++)
 {
   print MYOUTFILE "aaaa$j.$zone AAAA \n";
 }

 for( my $j=1;$j<=100; $j++)
 {
   print MYOUTFILE "cname$j.$zone CNAME \n";
 }
 for( my $j=1;$j<=100; $j++)
 {
   print MYOUTFILE "mx$j.$zone MX \n";
 }

 for( my $j=1;$j<=100; $j++)
 {
   print MYOUTFILE "txt$j.$zone TXT \n";
 }
 for( my $j=1;$j<=100; $j++)
 {
   print MYOUTFILE "srv$j.$zone SRV \n";
 }
 for( my $j=1;$j<=100; $j++)
 {
   print MYOUTFILE "dname$j.$zone DNAME \n";
 }
 for( my $j=1;$j<=100; $j++)
 {
   print MYOUTFILE "naptr$j.$zone NAPTR \n";
 }

 for( my $j=1;$j<=100; $j++)
 {
   print MYOUTFILE "ptr$j.$zone PTR \n";
 }
}
close(MYOUTFILE);

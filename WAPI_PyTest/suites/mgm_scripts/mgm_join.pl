 use strict;
 my $mgm_ip = $ARGV[0];
 my $gm_ip = $ARGV[1];
 my $gm_name = $ARGV[2];

system ("perl mgm.pl $mgm_ip $gm_name");
system ("perl join.pl $gm_ip $mgm_ip $gm_name");

print "\nJoin process is complted";


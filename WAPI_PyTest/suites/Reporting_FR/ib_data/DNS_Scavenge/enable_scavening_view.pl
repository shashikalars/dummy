 use strict;
 use Infoblox;
 my $host = $ARGV[0];
 my $session = Infoblox::Session->new(
     master   => $host,
     username => "admin",
     password => "infoblox"
     );
 unless( $session ){
     die("Constructor for session failed:",
     Infoblox::status_code() . ":" . Infoblox::status_detail());
 }
 print" Session object created successfully \n";

  my $expression1 = Infoblox::Grid::ExpressionOp->new(
     op       => 'AND',
     op1_type =>  'LIST',
 );


 my $expression2 = Infoblox::Grid::ExpressionOp->new(
      op1_type => 'FIELD',
        op2 => 'DYNAMIC',
        op2_type => 'STRING',
        op1 => 'rcreator',
        op => 'EQ'
 );


 my $expression3 = Infoblox::Grid::ExpressionOp->new(    op => 'ENDLIST' );

my $reclamation_setting = Infoblox::Grid::DNS::ScavengingSetting->new(
	enable_scavenging =>"true",
        expression_list   => [$expression1,$expression2, $expression3],       # Optional / Default is undefined
   );

for (my $m=1;$m<=2;$m++)
{
     my @result = $session->get(
     object => "Infoblox::DNS::View",
     name   => "view$m"
     );

 unless( @result ){
     die("Get grid DNS failed: ",
     $session->status_code() . ":" . $session->status_detail());
 }
 print" Get grid DNS object found at least 1 matching entry \n";


 my $grid_dns = $result[0];
 $grid_dns->scavenging_settings($reclamation_setting);
 $grid_dns->override_scavenging_settings('true');
 my $response = $session->modify($grid_dns);
  unless( $response ){
     die("Modify grid DNS failed: ",
     $session->status_code() . ":" . $session->status_detail());
			}

}

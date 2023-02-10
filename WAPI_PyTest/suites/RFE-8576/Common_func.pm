#!/usr/bin/perl
package Common_func;

use strict;
use Carp;
use Getopt::Std;
use Data::Dumper;
use Infoblox;

use Exporter;
our @ISA = qw(Exporter);
our @EXPORT = qw(   $co_session
                    co_create_session co_restart_service co_printDataStructure co_create_ifmap_session co_restart_status
                    
                    co_xmlapi_get co_get_view_list co_getHAstatus co_ipv6_compress
                    co_computenetmask co_special_char_conv
                    co_cidr_to_ipv6
                    co_cidr_to_ptr_ipv6
                    co_get_system_time
                    
                    co_printDataset co_printOperation co_printSummary 
                    co_printErrorMessage
                    populate_data
		    get_ipv6_option_name
                );
                
use vars qw( $co_session);

# Initial to 0
$co_session = 0;

# For old Internal API 
my %session_info = qw();

# ################################################################################
# ################################################################################

sub co_create_session
{
#  Create a session
#
#
   my($pAddressIP, $PUserName, $pPassWord, $pTimeout) = @_;
   my $lSession;
   
   $lSession = co_ooapi_open_session($pAddressIP, $PUserName, $pPassWord, $pTimeout);
   
   return $lSession;
}

sub co_ooapi_open_session
{
    my($dnsone_address, $username, $password, $timeout) = @_;
    my $code=0;
    my $status;
    
    my $waitcnt = 0;

    do {

	if (defined($timeout))
	{
	        $co_session = Infoblox::Session->new(
        	       "master" => $dnsone_address,
        	       "username" => $username,
	               "password" => $password,
		       "timeout" => $timeout );
	}
	else
	{
                $co_session = Infoblox::Session->new(
                       "master" => $dnsone_address,
                       "username" => $username,
                       "password" => $password );
	}
        $code = $co_session->status_code();
        if ($code != 0)
        {
            if ($waitcnt++ < 6) 
            {
                print "master https server not up, waiting 10 seconds to retry.\n";
                sleep (10);
            }
            else 
            {
                print("Session creation failed\n");
                $code = $co_session->status_code();
                $status = $co_session->status_detail();
                print "$code, $status\n";
                return(0);
            }
        }
    } while ($code != 0);

    return($co_session);
}

sub co_restart_service
{
#   Restart the service
#
#

    my $test_restart = shift; 
    my $member = shift;
	
    my %lData =
    (
#     "service" => "dns|dhcp",
#     "when" => "now", 
    );

    if ($test_restart eq "true") {
	$lData{"member"} = $member; 
	$lData{"test_restart"} = "true"; 
    }   

    my $lResult = $co_session->restart(%lData);
    sleep(10);
    return $lResult;
}


sub co_restart_status
{
#   Restart service status
#   Check for DNS/DHCP/Reporting service restart status and wait in a loop if RESTART_PENDING until restart complete. 	
#   This check introduced to avoid incorrect conf file validations (Ex: Validating conf file before it is updated with latest changes )
#
#   Input : Member IP to check service restart status on, service type like dns_status, dhcp_status, reporting_status etc.
#
    my $member = shift;
    my $stats = shift;

    my $retrieved_objs;
    if($member =~ /\:/) {
            $retrieved_objs = $co_session->get(
                   object => "Infoblox::Grid::Member",
                   ipv6addr => $member,
            );
    }
    else {
            $retrieved_objs = $co_session->get(
                   object => "Infoblox::Grid::Member",
                   ipv4addr => $member,
            );
    }

    my $member_hostname = $retrieved_objs->name();
    print "\nConf validation server hostname: $member_hostname\n";

    for ( my $count = 0; $count < 15; $count++ ) {
            my $lResult = $co_session->get(
                object => "Infoblox::Grid::Member::RestartServiceStatus",
                member => "$member_hostname",
            );

            if ( $lResult->$stats() eq "RESTART_PENDING" ) { print "\n Restart status pending, checking after 2 seconds"; }
            else { print "\nRestart $stats : ". $lResult->$stats() . "\n";  return 0; }
            sleep 2;
    }
}

sub co_create_ifmap_session
{
   my($session_param) = @_;
   my ($session_request, $response);
   my %param = %$session_param;
 
   my $client_hash = $param{"client"}; 
   my $client = Ifmap::Client->new(%$client_hash);

   if ( defined($param{"session_id"}) ) {
   	$session_request = Ifmap::Request::AttachSession->new( $param{"session_id"} );  # Re-connect to session created earlier.
   }
   else {
   	$session_request = Ifmap::Request::NewSession->new("max_poll_result_size"=>$param{"client"}{"max_poll_result_size"});
   }

   $response = $client->request($session_request);
    
   return ($client, $response);
}	

sub co_printDataStructure
{
#   Print the data structure -- Good for debug purpose
#
#
#
    my($pRefData, $pVarName) = @_;
    $Data::Dumper::Deepcopy = 1; # Avoid cross-refs
#    $Data::Dumper::Maxdepth = 5; # Avoid complete de-referencing
    $Data::Dumper::Sortkeys = \&my_filter;

    my $lPrintData = Data::Dumper->Dump([$pRefData], ["$pVarName"]);
    $lPrintData =~ s/[ ]{4}/ /g;
    print $lPrintData;
}

sub my_filter
{
    my ($hash) = @_;
    my %new_hash = %$hash;

    foreach (keys %new_hash) {
        if ($_ =~ m/(^__object_id_cache__)|(^__object_id__)|(^__ibap_common_members__)|(^__[^tv])/g) {
          delete $new_hash{$_};
        }
    }
    return [
          # Sort the keys
           (sort keys %new_hash)
        ];
}

################################################################################

sub co_computenetmask
{
#  Converts Oct form to Netmask
#
#  Example: /8 oct to 255.0.0.0 
#
#  Return: qw(255.0.0.0);
#
    my $subnet = shift;
    
    if( $subnet < 1 || $subnet > 32 )
    {
        print" Invalid subnet $subnet should be between ( 1 to 32 ) \n";
        return ( 0 );
    }
    
    my @octet;
    my $i;
    for( $i=0;$subnet > 0;$i++ )
    {
        if( ($subnet - 8) > 0 )
        {
            $octet[$i] = 8;
            $subnet = $subnet - 8 ;
        }
        else
        {
            $octet[$i] = $subnet;
            $subnet = $subnet - $subnet;
        }
    }
    
    my @netmask;
    my $j = 0;
    foreach my $oct ( @octet )
    {
        my $sum = 0;
        my $power = 0;
        my $numbit = 0;
        $numbit = $oct - 1;
        $power = 7;
        
        while( $numbit >= 0 )
        {
            $sum = $sum + (2 ** $power);
            $power = $power - 1;
            $numbit = $numbit- 1;
        }
        $netmask[$j] = $sum;
        $j++;
    }
    
    for( ; $j < 4 ; $j++ )
    {
        $netmask[$j] = 0;
    }
    
    my $actnetmask = join '.', @netmask;
    
    # print" ***********$actnetmask************\n";
    
    # print" netmask = $actnetmask \n";
    
    return( $actnetmask );
}

sub co_special_char_conv()
{
#  Converts special charators to replacement string, or replacement string to special charator.
#
#  Arguments:	co_special_char_conv(<intput string>);
#
#  Return: Converted String
#
  my $input = shift;
  my $output="";
  
  my $position = 0;
  my @str = split(//,$input);
  for (my $position=0;$position<@str;$position++)
  {
    my $cursor = $str[$position]; 
    if ($cursor eq "&")
    {
      my $rep;
      for(my $i = 1; $i < 6; $i++)
      {
        if ($str[$position+$i])
        {
          $rep = $rep.$str[$position+$i];
        }
      }
      if (substr($rep, 0, 4) eq "amp;")
      {
        $cursor = "&";
        $position = $position + 4;
      }
      elsif (substr($rep, 0, 3) eq "gt;")
      {
        $cursor = ">";
        $position = $position + 3;
      }
      elsif (substr($rep, 0, 3) eq "lt;")
      {
        $cursor = "<";
        $position = $position + 3;
      }
      elsif (substr($rep, 0, 5) eq "quot;")
      {
        $cursor = "\"";
        $position = $position + 5;
      }
      else
      {
        $cursor = "&amp;";
      }
    }
    elsif ($cursor eq ">")
    {
      $cursor = "&gt;";
    }
    elsif ($cursor eq "<")
    {
      $cursor = "&lt;";
    }
    elsif ($cursor eq "\"")
    {
      $cursor = "&quot;";
    }
    
    $output = $output.$cursor;
  }
  
  return($output);
}


##################################################################################

# This function will get the Name and IP of the unit in 4x builds.
#
# Input : 
#        member_primary => "x"  x = 0,1,2,3,4.....
# Author
#       Gururaj V Nidoni   ( 06/08/2006 )

################################################################################
sub co_xmlapi_get
{
    my $obj_to_get = shift;
    my $temp_args = shift;
    
    if ($obj_to_get eq "virtual_node")
    {
        my $session = $co_session;
        my $virtual_node = $temp_args;
        
        if ($virtual_node eq "")
        {
            print "Virtual node not specified to select\n";
            return(0);
        }
        
        my $xmlt_request = Infoblox::XmltRequest->new();
        my $xmlt_function = Infoblox::XmltFunction->new();
        $xmlt_function->set_function_name( ".com.infoblox.one.get_virtual_nodes" );
        my $xmlt_object = Infoblox::XmltObject->new();
        $xmlt_object->set_collection_name( "__default" );
        $xmlt_object->set_properties( "chunk" => "start=0,page_size=0" );
        $xmlt_function->append_element( $xmlt_object );
        $xmlt_request->append_element( $xmlt_function );
        
        my $content = $xmlt_request->as_string;
        
        my $https_req = $session->get_https_request();
        $https_req->content( $content );
        my $ua = LWP::UserAgent->new;
        my $https_response = $ua->request( $https_req );
        my $res_content = $https_response->content;
        
        my $xmlt_parser = Infoblox::XmltParser->new();
        my $xmlt_response = $xmlt_parser->parse( $res_content );
        $xmlt_function = $xmlt_response->element_at(0);
        
        my $virtual_nodes = $xmlt_function->get_element("virtual_nodes");
        
        my $elements = \@{$virtual_nodes->{ELEMENTS}};
        
        my @nodes = @$elements;
        foreach my $vn (@nodes)
        {
            if ($$vn{PROPERTIES}{virtual_oid} eq $virtual_node)
            {
                return (1, $vn);
            }
        }
        
        print "virtual node \"$virtual_node\" does not exist in this cluster.\n";
        return(0);
    }
}


###################################################################################
# Function:     co_get_system_time
#
# Description:  - Get system time on client machine and convert to ISO 8061 format 
#                 after adding offset from current time
#
# Arguments:    - co_get_system_time(<time offset (in seconds)>);
#
# Return        - scheduled time in ISO 8061 format
#
# Authors: Peter Lee and Sridharan Muthuswamy (01/07/2009)
##################################################################################


sub co_get_system_time
{

   my $offset_seconds = $_[0];

   my $current_time_seconds = `date +%s`;
   chomp ($current_time_seconds);
   my $scheduled_time_seconds = $current_time_seconds + $offset_seconds;
   my $scheduled_time_string = `date -d "1970-01-01 $scheduled_time_seconds sec" +%FT%TZ`;
   chomp($scheduled_time_string);

   return $scheduled_time_string;
}

###############################################################
#Function:     co_getHAstatus()
#
#Description:  - Get Active and Passive IP of an HA pair in cluster
#
#Arguments:    - ib_xmlapi_getHA_status(<HA VIP>);
#
#Return        - 0 on success, $active_ip, $passive_ip
#              - 1 on failure
# created by : Peter Lee
###################################################################

sub co_getHAstatus
{
    my ($ha_vip, $data_hash) = @_;
    
    my $session = $co_session;
    my %mem_hash = %{$data_hash};
    my $mem_name = $mem_hash{"name"};

    my @virtual_node = $session->get( "object" => "Infoblox::Grid::Member", "name" => $mem_name);
                    
    if ((scalar(@virtual_node) > 0)&&(ref($virtual_node[0]) eq "Infoblox::Grid::Member"))
    {
        my %mem_obj = %{$virtual_node[0]};
        if ($mem_obj{"ipv4addr"} eq $ha_vip)
            {
                my ($active_ip, $passive_ip);
                if ($mem_obj{"active_position"} eq "0")
                    {
                        $active_ip = $mem_obj{"node1_lan"};
                        $passive_ip = $mem_obj{"node2_lan"};
                    }
                    elsif ($mem_obj{"active_position"} eq "1")
                    {
                        $active_ip = $mem_obj{"node2_lan"};
                        $passive_ip = $mem_obj{"node1_lan"};
                    }
                    else
                    {
                        return (1); #not HA mode
                    }
            return (0, $active_ip, $passive_ip);
            }
    }else{
	return(1); # Unable to retrieve member properties.
   }

}



###########################################################
#   Name: co_get_view_list()                              #
#   Description: This sub routine will retrive named.conf #
#                from an appliance and find out the order #
#                of all the Bind Views on the named.conf. #
#                                                         #
#   Argument: VIP/IP of appliance                         #
#   output:   Array containing all Bind Views on the      #
#             appliance, ordered from the first found     #
#             view to last found view.                    #
###########################################################
sub co_get_view_list
{
    my $server_ip = shift;
    my @views;


    # check whether the server is accessible for download.
    my $error_count_conf=0;
    my $dumpDir = "./dump";
    system ("mkdir -p $dumpDir");
    my $config_file="$dumpDir/downloadedFile.$$";
    my $serverConfigFileName = "/infoblox/var/named_conf/named.conf";
    my $sshOutput =  system ("ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root\@$server_ip /bin/true");
    my $sshResult = $?;
    if ($sshResult != 0)
    {
        print "ERROR: Unable to ssh into the server $server_ip.  Error!!!\n";
    }
    else
    {
        if (-e $config_file) {system ("rm -rf $config_file");}
        # download the given file from the server to the local /dump direcotry
        $sshOutput = system("scp -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root\@$server_ip:$serverConfigFileName $config_file");
        $sshResult = $?;
        if ($sshResult != 0)
        {
            print "ERROR: Unable to find file $serverConfigFileName in the server $server_ip.  Error!!!\n";
        }
        else
        {
            print "File is downloaded to $config_file\n";
            
            my @conf_clients;
            my @conf_recursion;
            
            open(NAMED, "<$config_file") || die "can't open the file '$config_file'";
            my(@input) = <NAMED>;
            close (NAMED) || die "couldn't close file: $config_file\n";
            my @view_statement;
            my $view_found = "0";
            my $last_line;
            for (my $i = 0; $i < scalar(@input); $i++)
            {
                my $curline = $input[$i];
                my $line = $curline;
                chop ($line);
                my $tmp_view;
                if(($line =~ m/view.*/) && ($last_line =~ m/{.*#\s*(.*)/))
                {    # check if line contains zone name.
                    $tmp_view = $1;
                    print "$tmp_view\n";
                    push @views, $tmp_view;
                }
                $last_line = $line;
            }
        }
    }
    
    return @views;
}

########################################################################
# Function Name: co_printOperation
#
# Description:
#    This function help print out an operation result along with the
#    and the executed result.  The executed result is the result per the
#    execution. The final result is determined by the expected and executed
#    results.  This result will print out the a message as according to
#    the condition below.
#
#    Expected | Executed | Final Result
#    ---------------------------------------
#    PASS     | PASS     | Pass as expected.
#    PASS     | FAIL     | Fail as unexpected.
#    FAIL     | PASS     | Pass as unexpected.
#    FAIL     | FAIL     | Fail as expected.
#
#    A description will get print out before the operation result.
#
#
# Input Options:
#   co_printOperation <utilityname> <descripiton> <expected> <executed> <log> <flagtype>
#
#
#    utilityname - required field, is the name of the program that call this function.
#    descripiton - required field, is the title of the operation or any description you want to dislay.
#    expected - required field, is the result you expect. 0 means pass while 1 means fail.
#               If this parameter passes in a string "positive" or "negative," it will automaticly
#               get converted into "0" for pass and "1" for fail. 
#    executed - required field, is the result return from an operation. This result
#               start with 1 for pass while 0 for fail. 
#    log -      required field, is the error message you want to display.
#    flagtype - required field, it can be "DESC", "RESULT", "LOG", or "DEFAULT".
#               The default flagtype is "DEFAULT."  NULL input for this field
#               will reset to use default.
#               When flagtype is "DESC," this function only prints out the "DESC" section.
#               When flagtype is "RESULT," this function only prints out the "RESULT" secion.
#               When flagtype is "LOG," this function only prints out the "LOG" section.
#               When flagtype is "DEFAULT," this function will print out section. The order
#               it get print out is "DESC" section, "LOG" section, and "RESULT" section.
#
#
# Example: To print out the operation result along with file name, description,
#          log message, and final result.
#
#   co_printOperation("add_a.pl", "Add duplicate A record", "negative", "negative"
#                     "0, Adding a duplicate A record fail", "DEFAULT");
#
# Output:
#
# <<OPERATION: add_a.pl, Add duplicate A record>>
#   EXECUTION: 0, Adding a duplicate A record fail
# ++RESULT per OPERATION: Fail as expected.
#
#
# Author: Troi Ho
#
# History:
#    07/25/06 (Troi Ho) - Created
########################################################################
sub co_printOperation
{
    my($pFileName, $pDesc, $pExpect, $pExecute, $pLog, $pFlag) = @_;
    my $lSpace = "          "; # Default: 10 space index;
    my $lFlag;
    my $lExpect;
    my $lExecute;

    if (!defined($pExecute))
    {
        $pExecute = 0;
    }
    
    # Overall Parameters check
    if( !defined($pFileName) || !defined($pDesc) || !defined($pExpect) ||
        !defined($pExecute) || !defined($pLog) || !defined($pFlag)
      )
    {
        print "<<OPERATION: $pFileName, $pDesc>>\n";
        print "ERROR: Detect invalid parameters.\n\n";
        return 1; # return fail
    }
    
    # Error check
    if( !(&co_isDigit($pExpect)) )
    {   # Not a digit yet
        # Input is string (positive/negative)
        $lExpect = ($pExpect eq "positive") ? 0 : 1;  # We use 0 for PASS
    }
    
    if( (&co_isDigit($pExecute)) )
    {   # Input is digit -> convert to QE Pass/Fail logic
        $lExecute = ($pExecute == 1) ? 0 : 1;  # Engineer use 1 for PASS
    }
    else
    {   # Not a digit yet
        # Input is digit
        $lExecute = ($pExecute eq "positive") ? 0 : 1;
    }
    
    if( !(&co_isDigit($lExpect)) || !(&co_isDigit($lExecute)) )
    { # Not a number
        print "<<OPERATION: $pFileName, $pDesc>>\n";
        print "ERROR: Detect invalid parameters.\n\n";
        return 1; # Fail
    }
    
    $lFlag = $pFlag;
    if( $pFlag eq "" )
    { # Assume DEFAULT
        $lFlag = qq{DEFAULT};
    }
    
    chomp($pLog);
    
    if( $lFlag eq "DESC" )
    { # Print out DESC only
        print "<<OPERATION: $pFileName, $pDesc>>\n";
        return 0; # Pass
    }
    elsif( $lFlag eq "RESULT" )
    {   # Print out Result only
        print "EXECUTION:    $pLog\n";
        
        if( $lExecute == 0 )
        {  # Actual Pass
            if($lExpect == $lExecute)
            {
                print "++RESULT per OPERATION:    Pass as expected.\n\n";
                return 0; # Pass
            }
            else
            {
                print "++RESULT per OPERATION:    Pass as unexpected.\n\n";
                return 1; # Fail
            }
        }
        if( $lExecute == 1 )
        { # Actual Fail
            if($lExpect == $lExecute)
            {
                print "++RESULT per OPERATION:    Fail as expected.\n\n";
                return 0; # Pass
            }
            else
            {
                print "++RESULT per OPERATION:    Fail as unexpected.\n\n";
                return 1; # Fail
            }
        }
    }
    elsif( $lFlag eq "LOG" )
    { # Print out log only
        print "EXECUTION: $pLog\n\n";  # 10 space index;
        return 0;
    }
    elsif( $lFlag eq "DEFAULT" )
    { # DEFAULT is assumed
        my $lResultText;
        
        # Print out Description
        print "<<OPERATION: $pFileName, $pDesc>>\n";
        print "EXECUTION:    $pLog\n";
        
        if( $lExecute == 0 )
        {  # Actual Pass
            if($lExpect == $lExecute)
            {
                print "++RESULT per OPERATION:    Pass as expected.\n\n";
                return 0; # Pass
            }
            else
            {
                print "++RESULT per OPERATION:    Pass as unexpected.\n\n";
                return 1; # Fail
            }
        }
        if( $lExecute == 1 )
        { # Actual Fail
            if($lExpect == $lExecute)
            {
                print "++RESULT per OPERATION:    Fail as expected.\n\n";
                return 0; # Pass
            }
            else
            {
                print "++RESULT per OPERATION:    Fail as unexpected.\n\n";
                return 1; # Fail
            }
        }
    }
    
    print "<<OPERATION: $pFileName, $pDesc>>\n";
    print "ERROR: Detect invalid parameters.\n\n";
    return 1; # return fail
}

########################################################################
# Function Name: co_printDataset
#
# Description:
#    This function help print out a data structure of a scalar,
#    hash, array, associative array, or an object.  A description is displayed
#    first before the dataset.
#
#
# Input Options:
#    co_printDataset <dataset> <datafile> <index> <description>
#
#    dataset - require field, a reference to any data type needs to print out.
#    datafile - require field, the file name that contain the dataset.
#    index - require field, an index number point to a dataset variable.
#            The index number is always a positive number starting with 1.
#
#    description - require field, a string of text identifying the dataset
#
#
#
# Example: To print out a dataset with file name, index, and description
#
#    &co_printDataset(\%ooapi_data_hash, "data_set/3_2_11/DNS3_1r1-3_2_11_1-4", 0, "Add an A record");
#
# Output:
#
# <<DATASET: data_set/3_2_11/DNS3_1r1-3_2_11_1-4, 1, Add an A record>>
# $RefData1 = {
#              'ipv4addr' => '10.0.0.250',
#              'name' => 'h000000000001.ddnszone.test.com'
#              };
#
#
# Author: Troi Ho
#
# History:
#    07/25/06 (Troi Ho) - Created
########################################################################
sub co_printDataset
{
    my($pRefData, $pFileName, $pIndex, $pDesc) = @_;
    my $lIndex;
    
    # Print out title
    chomp($pDesc);
    
    # Check Parameters for invalid entry
    if( !(ref($pRefData)) || !($pIndex =~ m/^[\d+|n]$/g) && !defined($pFileName) &&
        !defined($pIndex) && !defined($pDesc) )
    {
        print "<<DATASET: >>\n";
        print "ERROR: Detect invalid parameters.\n\n";
    }
    
    print "<<DATASET: $pFileName, $pIndex, $pDesc>>\n";
    # Print out dataset structure
    &co_printDataStructure($pRefData, qq{RefData$pIndex});
    print "\n\n";
    
    return 0; # Okay
}

########################################################################
#
# Function Name: co_printSummary
#
# Description:
#    At the end of each utility, this function should be called to print out
#    the overall result of the operation or validation.
#
#
# Input Options:
#    co_printSummary <flag>
#
#    Flag - require field, this field needs to be an positive number and must
#           be either 0 or 1.  0 means pass while 1 means fail.
#
#
# Example: To print out the final result before exiting the program.
#
#    &co_printSummary(0);
#
#
# Output:
#
# <<<<<SUMMARY>>>>>
# ++RETURN: 0 (Passed)
#
#
# Return:
#    0: Success
#    1: Failed
#
#
# Author: Troi Ho
#
# History:
#    07/25/06 (Troi Ho) - Created
########################################################################
sub co_printSummary
{
    my($pFlag) = @_;
    
    print "<<<<<SUMMARY>>>>>\n";
    if( &co_isDigit($pFlag) )
    {
        if( $pFlag == 0 )
        {
          # print "0123456789\n";
            print "++RETURN: 0 (Passed)\n\n";
            return 0; # Return Pass
        }
        if($pFlag == 1)
        {
          # print "0123456789\n";
            print "++RETURN: 1 (Fail)\n\n";
            return 1; # return fail
        }
    }
    
    print "Error: Detect invalid parameters.\n\n";
    return 1; # return fail
}

########################################################################
#
# Function Name: co_printErrorMessage
#
# Description:
#    This function help to print out any error message. (eg non-operational errors)
#    It also print out a description for this message at the beginning.
#
# Input Options:
#    co_printErrorMessage <message> [description]
#    
#    message - require field, Error message you want to print
#    description - optional field, Description of this message
#
#
# Example: To print out an error message occur if a specific file is not found.
#
#    &co_printErrorMessage("Open File Error", "Open file not found, DNS3_1r1-3_2_11_1-2");
#
# Output:
#
# <<MESSAGE: Open File>>
# --ERROR: Open file not found, DNS3_1r1-3_2_11_1-2
#
#
# Author: Troi Ho
#
# History:
#    07/25/06 (Troi Ho) - Created
########################################################################
sub co_printErrorMessage
{
    my($pDesc, $pMsg) = @_;

    chomp($pMsg);
    chomp($pDesc);
    
    if( !defined($pMsg) || ($pMsg eq "") ||
        !defined($pDesc) || ($pDesc eq "") )
    {
        print "<<MESSAGE: >>\n";
        print "ERROR: Detect invalid parameters.\n\n";
        return 1; # return fail
    }
    
    print "<<MESSAGE: $pDesc>>\n";
    print "ERROR: $pMsg\n\n";
    return 0; # return okay
}

sub co_isDigit
{
# Return 1 if data is digit
#        0 if not digit
#
    my ($pData) = @_;
    my $lDigit;
    
    $lDigit = $pData;
    if( $lDigit =~ m/^\d+$/g)
    { # It is a digit
        return 1;
    }
    return 0; # Not a digit
}







#generate data based on the data type and seed
sub generate_data
{
    my $data_type = shift;
    my $seed = shift;
    
    
    #generate string.
    #seed 1 will generate string "a".
    #seed 2 will generate string "b".
    #.
    #.
    #.
    #Seed 27 will generate string "aa"
    #Seed 28 will generate string "ab"
    if ($data_type eq "GEN_STRING")
    {
        my @chars = ("a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z" );
        
        my $generated_string;
        my $cursor = $seed - 1;
        while ($cursor >= scalar(@chars))
        {
            my $current_char = $cursor % scalar(@chars);
            $generated_string = $chars[$current_char] . $generated_string;
            $cursor = ($cursor - $current_char) / scalar(@chars);
	    if( $cursor >= 1 )
	    {
		$cursor -= 1;
	    }
        }
       	$generated_string = $chars[$cursor] . $generated_string;

        return $generated_string;
    }
    
    
    
    #generate integer, simple return the seed since seed is integer.
    if ($data_type eq "GEN_INT")
    {        
        return $seed;
    }
    
    
    
    #generate octecs.
    #seed 1 will generate ip "1.0.0.1".
    #seed 2 will generate ip "1.0.0.2".
    #.
    #.
    #.
    #Seed 256 will generate ip "1.0.1.0"
    #Seed 257 will generate ip "1.0.1.1"
    #the return result will always have at least 1 in the first octect, because use may try to use it in the beginning of the IP.
    if ($data_type =~ m/GEN_(\d+)_OCT/)
    {
        my $octs = $1;
        my $ip_string;
        my $oct1 = 1;
        my $oct2 = 0;
        my $oct3 = 0;
        my $oct4 = 0;
        
        $oct4 = $seed % 256;
        $seed = ($seed - $oct4) / 256;
        $oct3 = $seed % 256;
        $seed = ($seed - $oct3) / 256;
        $oct2 = $seed % 256;
        $seed = ($seed - $oct2) / 256;
        $oct1 = ($seed % 256);
        
        if ($octs == 1)
        {
            return $oct4 + 1;
        }
        if ($octs == 2)
        {
            return $oct3 + 1 . ".$oct4";
        }
        if ($octs == 3)
        {
            return $oct2 + 1 . ".$oct3.$oct4";
        }
        if ($octs == 4)
        {
            return $oct1 + 1 . ".$oct2.$oct3.$oct4";
        }
    }

    if ($data_type =~ m/GEN_(\d+)_HEX/)
    {
        my $octs = $1;
        my $ip_string;
        my $oct1 = 1;
        my $oct2 = 0;
        my $oct3 = 0;
        my $oct4 = 0;
        my $oct5 = 0;
        my $oct6 = 0;
        my $oct7 = 0;
        my $oct8 = 0;
	my $rest_tups;
	my ( $tup1, $tup2, $tup3, $tup4, $tup5, $tup6, $tup7, $tup8 );

        $oct8 = $seed % 65536;
        $seed = ($seed - $oct8) / 65536;
        $oct7 = $seed % 65536;
        $seed = ($seed - $oct7) / 65536;
        $oct6 = $seed % 65536;
        $seed = ($seed - $oct6) / 65536;
        $oct5 = ($seed % 65536);
        $seed = ($seed - $oct5) / 65536;
        $oct4 = $seed % 65536;
        $seed = ($seed - $oct4) / 65536;
        $oct3 = $seed % 65536;
        $seed = ($seed - $oct3) / 65536;
        $oct2 = $seed % 65536;
        $seed = ($seed - $oct2) / 65536;
        $oct1 = ($seed % 65536);

        if ($octs == 1)
        {
            $tup8 = sprintf("%x",$oct8+1);
            return $tup8;
        }
        if ($octs == 2)
        {
            $rest_tups = sprintf("%x",$oct8);
            $tup7 = sprintf("%x",$oct7+1);
            return $tup7 . ":$rest_tups";
        }
        if ($octs == 3)
        {
            $rest_tups = sprintf("%x.%x",$oct7, $oct8);
            $tup6 = sprintf("%x",$oct6+1);
            return $tup6 . ":$rest_tups";
        }
        if ($octs == 4)
        {
            $rest_tups = sprintf("%x.%x.%x",$oct6, $oct7, $oct8);
            $tup5 = sprintf("%x",$oct5+1);
            return $tup5 . ":$rest_tups";
        }
        if ($octs == 5)
        {
            $rest_tups = sprintf("%x.%x.%x.%x",$oct5, $oct6, $oct7, $oct8);
            $tup4 = sprintf("%x",$oct4+1);
            return $tup4 . ":$rest_tups";
        }
        if ($octs == 6)
        {
            $rest_tups = sprintf("%x.%x.%x.%x.%x",$oct4,$oct5, $oct6, $oct7, $oct8);
            $tup3 = sprintf("%x",$oct3+1);
            return $tup3 . ":$rest_tups";
        }
        if ($octs == 7)
        {
            $rest_tups = sprintf("%x.%x.%x.%x.%x.%x",$oct3, $oct4,$oct5, $oct6, $oct7, $oct8);
            $tup2 = sprintf("%x",$oct2+1);
            return $tup2 . ":$rest_tups";
        }
        if ($octs == 8)
        {
            $rest_tups = sprintf("%x.%x.%x.%x.%x.%x.%x",$oct2, $oct3, $oct4,$oct5, $oct6, $oct7, $oct8);
            $tup1 = sprintf("%x",$oct1+1);
            return $tup1 . ":$rest_tups";
        }

    }

    if ($data_type =~ m/GEN_(\d+)_MAC/)
    {
        my $hex = $1;
        my $ip_string;
        my $hex1 = 0;
        my $hex2 = 0;
        my $hex3 = 0;
        my $hex4 = 0;
        my $hex5 = 0;
        my $hex6 = 0;
        my $rest_tups;
        my ( $tup1, $tup2, $tup3, $tup4, $tup5, $tup6 );

        $hex6 = $seed % 256;
        $seed = ($seed - $hex6) / 256;
        $hex5 = ($seed % 256);
        $seed = ($seed - $hex5) / 256;
        $hex4 = $seed % 256;
        $seed = ($seed - $hex4) / 256;
        $hex3 = $seed % 256;
        $seed = ($seed - $hex3) / 256;
        $hex2 = $seed % 256;
        $seed = ($seed - $hex2) / 256;
        $hex1 = ($seed % 256);

         if ($hex == 1)
        {
            $tup6 = sprintf("%x",$hex6);
            return $tup6;
        }
        if ($hex == 2)
        {
            $rest_tups = sprintf("%x",$hex6);
            $tup5 = sprintf("%x",$hex5);
            return $tup5 . ":$rest_tups";
        }
        if ($hex == 3)
        {
            $rest_tups = sprintf("%x:%x",$hex5, $hex6);
            $tup4 = sprintf("%x",$hex4);
            return $tup4 . ":$rest_tups";
        }
        if ($hex == 4)
        {
            $rest_tups = sprintf("%x:%x:%x",$hex4, $hex5, $hex6);
            $tup3 = sprintf("%x",$hex3);
            return $tup3 . ":$rest_tups";
        }
        if ($hex == 5)
        {
            $rest_tups = sprintf("%x:%x:%x:%x",$hex3, $hex4, $hex5, $hex6);
            $tup2 = sprintf("%x",$hex2);
            return $tup2 . ":$rest_tups";
        }
        if ($hex == 6)
        {
            $rest_tups = sprintf("%x:%x:%x:%x:%x",$hex2,$hex3, $hex4, $hex5, $hex6);
            $tup1 = sprintf("%x",$hex1);
            return $tup1 . ":$rest_tups";
        }

     }
    return $data_type;
}


# parse through the hash and find what if any data needs to be populated.
sub populate_data
{
    my $seed = shift;
    my $ref_obj = shift;
    my %data = %{$ref_obj};
    
    foreach my $attr (keys %data)
    {

	if( !ref($data{$attr}) )
	{
		$data{$attr} = gen_scalar( $seed , $data{$attr} ); 
	}
        elsif( ref($data{$attr}) eq "ARRAY" )
        {
                $data{$attr} = gen_array($seed,  $data{$attr});
	}
	elsif( ref($data{$attr}) eq "HASH" )
	{
                $data{$attr} = gen_hash($seed,  $data{$attr});
	}

    }
    
    return \%data;

}

sub gen_array
{

	my $seed = shift;
	my $arr_ele = shift;

	my @data_array = @{$arr_ele};

	foreach my $read ( @data_array )
	{
		if( !ref($read) )
		{
			foreach my $attr ( @data_array )
			{
				$attr = gen_scalar( $seed , $attr );
			}
		}
		elsif (ref($read) eq "ARRAY")
		{
                        foreach my $attr ( @data_array )
                        {
                                $attr = gen_array( $seed , $attr );
                        }
		}
		else
		{
                        foreach my $attr ( @data_array )
                        {
                                $attr = gen_hash( $seed , $attr );
                        }
		}
	}
	return \@data_array;
}


sub gen_hash
{
        my $seed = shift;
        my $hash_ele = shift;

        my %data_hash = %{$hash_ele};

        foreach my $read ( %data_hash )
        {
                if( !ref($read) )
                {
                        foreach my $attr ( %data_hash )
                        {
                                $attr = gen_scalar( $seed , $attr );
                        }
                }
                elsif (ref($read) eq "ARRAY")
                {
    #                    foreach my $attr ( %data_hash )
    #                    {
                                $read = gen_array( $seed , $read );
    #                    }
                }
                else
                {
    #                    foreach my $attr ( %data_hash )
    #                    {
                                $read = gen_hash( $seed , $read );
    #                    }
                }       
        }       
        return \%data_hash;

}


sub gen_scalar
{

	my $seed = shift;
	my $attr_value = shift;
        while ($attr_value =~ m/GEN_(\S+)/)
        {
            my $tmp_seed = $seed;
            my $gen_data_type = $1;
            my $additional_op;           # this is for if the dataset specifies to add or minus the seed.. (eg. +1 or -1)
            if ($gen_data_type =~ m/STRING(\S*)/)
            {
                $additional_op = $1;     # additional operation needs to be connected with no space with the keyword.
                $gen_data_type = "GEN_STRING";
            }
            elsif ($gen_data_type =~ m/INT(\S*)/)
            {
                $additional_op = $1;     # additional operation needs to be connected with no space with the keyword.
                $gen_data_type = "GEN_INT";
            }
            elsif ($gen_data_type =~ m/^(\d+)_OCT(\S*)/)
            {
                $additional_op = $2;     # additional operation needs to be connected with no space with the keyword.
                $gen_data_type = "GEN_$1_OCT";
            }
            elsif ($gen_data_type =~ m/^(\d+)_HEX(\S*)/)
            {
                $additional_op = $2;     # additional operation needs to be connected with no space with the keyword.
                $gen_data_type = "GEN_$1_HEX";
            }
	    elsif ($gen_data_type =~ m/^(\d+)_MAC(\S*)/)
            {
                $additional_op = $2;     # additional operation needs to be connected with no space with the keyword.
                $gen_data_type = "GEN_$1_MAC";
            }
            else
            {
                $gen_data_type = "UNKNOW_DATA_TYPE";
            }

            if ($additional_op =~ m/(\++[0-9]+)(.*)|(\-+[0-9]+)(.*)/)   # this is to ensure additional operation doesn't get mixed up with other text connected.
            {
                $additional_op = $1;
                $tmp_seed .= $additional_op;
                $tmp_seed = eval($tmp_seed);
            }
            else
            {
                $additional_op = "";
            }

            my $pop_data = &generate_data($gen_data_type, $tmp_seed);
            my $replace_string = $gen_data_type . $additional_op;  # need this so the replace action won't replace other connected text.
            $replace_string =~ s/\+/\\+/;  # need to escape the +/-, else it won't replace.
            $replace_string =~ s/\-/\\-/;
            $attr_value =~ s/$replace_string/$pop_data/;
        }
	return $attr_value;

}

sub co_cidr_to_ipv6
{
#  Covert cidr IPv6 to Ipv6 zone format
#  10::/32 -> 0.1.0.0.0.1.0.0.ip6.arpa
#
#
    my ($pData) = @_;
    my @hex_arr;
    my $first_part;
    my $last_part;
    my($ip_address, $s_mask) = split "\/", $pData;
    if ( $ip_address =~ m/::/ ) {
	    ($first_part, $last_part) = split "::",$ip_address;
    }
    elsif ( $ip_address =~ m/:/ ) {
            @hex_arr = split ":",$ip_address;	# Need to implement additional logic for ':'  IPv6 addresses
    }

    my ($sz1,$f_indot) = co_conv2dot($first_part);
    my ($sz2,$s_indot) = co_conv2dot($last_part);
    my $tot_sz = $sz1 + $sz2;

    my $ipv6_arpa = $f_indot;		

    my $rem = 8 - $tot_sz;
    for (my $c =0; $c<$rem;$c++)
    {
        $ipv6_arpa = "0.0.0.0".".".$ipv6_arpa;		# Add additional dots required for IPv6 format
    }

    my $op_ipv6_format = $s_indot.".".$ipv6_arpa;
    my $hexes = $s_mask/4;
    my @ipv6_hex = split ('\.', $op_ipv6_format);
    my $length = scalar(@ipv6_hex) - $hexes;		# Depending on netmask decide how many hexes to be included
    splice (@ipv6_hex, 0, $length);
    my $oct_ipv6_format = join('.', @ipv6_hex);
    $oct_ipv6_format = $oct_ipv6_format . "." . "ip6.arpa";

    return $oct_ipv6_format;
}

sub co_cidr_to_ptr_ipv6
{
#   Convert: IPv6 address to IPv6 PTR
#   12:34::a8  -> 8.a.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.4.3.0.0.2.0.0.0.ip6.arpa
#
    my ($pData) = @_;
    my ($first_part,$last_part) = split "::",$pData;
    
    my ($sz1,$f_indot) = co_conv2dot($first_part,);
    my ($sz2,$s_indot) = co_conv2dot($last_part);
    
    my $tot_sz = $sz1 + $sz2;
    
    my $ipv6_arpa = $f_indot."."."ip6.arpa";
    
    my $rem= 8 - $tot_sz;
    
    for (my $c =0; $c<$rem;$c++)
    {
        $ipv6_arpa = "0.0.0.0".".".$ipv6_arpa;
    }
    
    my $op_ipv6_format = $s_indot.".".$ipv6_arpa;
    
    #print "Return Value: $op_ipv6_format\n";
    return $op_ipv6_format;
}

sub co_conv2dot
{
#  sub routine call for cidr_to_ptr_ipv6
#  Help covert IPv6 address to PTR IPv6 only
#
#
    my $part = shift;
    
    my @hex_arr = split ":",$part;
    my @reverse =reverse@hex_arr;
    
    my $cnt;
    
    my @ipv6_arr;
    
    foreach (@reverse)
    {### reverse of the array of ips 34 12
        $_ = reverse $_;     ## 43 then 21
        my @octs = split //,$_;
        my $ip_for = $octs[0];
        my $i;
        for ($i =1;$i<@octs;$i++)
        {
            $ip_for = $ip_for.".".$octs[$i]; 
        }
        while($i<4)
        {
            $ip_for = $ip_for.".".0;
            $i++;
        }
        push @ipv6_arr, $ip_for;
    }
    
    my $ipv6_arpa = $ipv6_arr[0];
    
    for (my $i =1;$i<@ipv6_arr;$i++)
    {
        $ipv6_arpa = $ipv6_arpa.".".$ipv6_arr[$i]; 
    }
    
    $cnt = @ipv6_arr;
    return ($cnt,$ipv6_arpa);
}


#give a ipv6 option#, return you the ipv6 option name that would appear on conf file.
#If it's a custom option with no name, it will return you the option# back. which would also appear on conf file.
sub get_ipv6_option_name
{
  my $opt_num = shift;

  my %opt_list = (
		2 => "dhcp6.server-id",
		7 => "dhcp6.preference",
		12 => "dhcp6.unicast",
		14 => "dhcp6.rapid-commit",
		21 => "dhcp6.sip-servers-names",
		22 => "dhcp6.sip-servers-addresses",
		23 => "dhcp6.name-servers",
		24 => "dhcp6.domain-search",
		27 => "dhcp6.nis-servers",
		28 => "dhcp6.nisp-servers",
		29 => "dhcp6.nis-domain-name",
		30 => "dhcp6.nisp-domain-name",
		31 => "dhcp6.sntp-servers",
		32 => "dhcp6.info-refresh-time",
		33 => "dhcp6.bcms-server-d",
		34 => "dhcp6.bcms-server-a",
		39 => "dhcp6.fqdn",
  );

  if (defined $opt_list{$opt_num})
  {
    return $opt_list{$opt_num};
  }
  else
  {
    return $opt_num;
  }
}


###################################################################


sub co_ipv6_compress
{
    my $ipv6_string = shift;
    my @arr = map { hex } split /:/, $ipv6_string;
    my $expanded = join(":", map { sprintf("%x", $_) } @arr);
    $expanded =~ s/^0:/:/;
    $expanded =~ s/:0/:/g;
    if ($expanded =~ s/:::::::/_/ or
        $expanded =~ s/::::::/_/ or
        $expanded =~ s/:::::/_/ or
        $expanded =~ s/::::/_/ or
        $expanded =~ s/:::/_/ or
        $expanded =~ s/::/_/
        ) {
        $expanded =~ s/:(?=:)/:0/g;
        $expanded =~ s/^:(?=[0-9a-f])/0:/;
        $expanded =~ s/([0-9a-f]):$/$1:0/;
        $expanded =~ s/_/::/;
    }
    $expanded =  lc($expanded);
    return $expanded;
}





1;

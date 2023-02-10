#!/usr/bin/perl

$time_limit = $ARGV[0];
$counter = 0;
$exit = 0;
print $time_limit . " is the Specified Time\n";

#$cisco_server_1 = "CISCO_ISE_SERVER_1";
$cisco_server_1 = "10.36.141.21";
#$cisco_server_2 = "CISCO_ISE_SERVER_2";
#$cisco_server_3 = "CISCO_ISE_SERVER_3";

#$Grid_PT1Member14="10.35.20.51";
#$Grid_Master_Candidate="10.35.1.222";

my @server_list = ("$cisco_server_1","$cisco_server_2","$cisco_server_3");
while (1)
{
        print "Inside the time Frame\n";
       	my $i = 1;
        while($counter < $time_limit)
        {
                foreach $server (@server_list)
                {
                        for($i=1;$i<=254;$i++)
                        {
                                system("cd /home/mreddy/Cisco-ISE/Radius;java -cp RadiusSimulator.jar -DUSERNAME=qa000001 -DPASSWORD=Infoblox1492 -DRADIUS_SECRET=infoblox -DFRAMED_IP_ADDRESS=10.1.0.$i -DFRAMED_IP_MASK=255.255.0.0 RadiusAccountingStart $server");
                                system("cd /home/mreddy/Cisco-ISE/Radius;java -cp RadiusSimulator.jar -DUSERNAME=qa000001 -DPASSWORD=Infoblox1492 -DRADIUS_SECRET=infoblox -DFRAMED_IP_ADDRESS=10.1.0.$i -DFRAMED_IP_MASK=255.255.0.0 RadiusAuthentication $server");
                                for($j=1;$j<=254;$j++)
                                {
                                        system("cd /home/mreddy/Cisco-ISE/Radius;java -cp RadiusSimulator.jar -DUSERNAME=qa000001 -DPASSWORD=Infoblox1492 -DRADIUS_SECRET=infoblox -DFRAMED_IP_ADDRESS=10.1.$i.$j -DFRAMED_IP_MASK=255.255.0.0 RadiusAccountingStart $server");
                                        system("cd /home/mreddy/Cisco-ISE/Radius;java -cp RadiusSimulator.jar -DUSERNAME=qa000001 -DPASSWORD=Infoblox1492 -DRADIUS_SECRET=infoblox -DFRAMED_IP_ADDRESS=10.1.$i.$j -DFRAMED_IP_MASK=255.255.0.0 RadiusAuthentication $server");                                
                                }
                        }
                        for($i=1;$i<=254;$i++)
                        {
                                for($i=1;$i<=254;$i++)
                                {
                                        #my $j=1; 
                                        for($a=1;$a<=254;$a++)
                                        {
                                                $j++;
                                                system("cd /home/mreddy/Cisco-ISE/Radius;java -cp RadiusSimulator.jar -DUSERNAME=qa000001 -DPASSWORD=Infoblox1492 -DRADIUS_SECRET=infoblox -DFRAMED_IP_ADDRESS=10.$i.$j.$a -DFRAMED_IP_MASK=255.255.0.0 RadiusAccountingStart $server");
                                                system("cd /home/mreddy/Cisco-ISE/Radius;java -cp RadiusSimulator.jar -DUSERNAME=qa000001 -DPASSWORD=Infoblox1492 -DRADIUS_SECRET=infoblox -DFRAMED_IP_ADDRESS=10.$i.$j.$a -DFRAMED_IP_MASK=255.255.0.0 RadiusAuthentication $server");
                                        }
                                }        
                        }
                                
                }
                    
        }
        $process=$$;
        $i++;
        if ($counter >= $time_limit){
                print "exinting as a time out\n\n\n\n\n\n\n";
                `sudo kill -9 $process`;
        }
        sleep 240;
        $counter+=240;
        print "Continuing the execution for next Day!!!\n\n\n\n";
}

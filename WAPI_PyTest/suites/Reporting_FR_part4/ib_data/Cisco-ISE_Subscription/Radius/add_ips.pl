#!/usr/bin/perl
my $i;
for ($i=1; $i<21; $i++){
`java -cp RadiusSimulator.jar -DUSERNAME=qa -DPASSWORD=Infoblox1492 -DRADIUS_SECRET=secret -DFRAMED_IP_ADDRESS=10.0.1.$i -DFRAMED_IP_MASK=255.255.255.0 RadiusAccountingStart 10.36.141.15 >/dev/tty`;
sleep 5;
`java -cp RadiusSimulator.jar -DUSERNAME=qa -DPASSWORD=Infoblox1492 -DRADIUS_SECRET=secret -DFRAMED_IP_ADDRESS=10.0.1.$i -DFRAMED_IP_MASK=255.255.255.0 RadiusAuthentication 10.36.141.15 >/dev/tty`
}

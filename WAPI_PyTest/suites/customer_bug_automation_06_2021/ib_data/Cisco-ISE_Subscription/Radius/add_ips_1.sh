#!/bin/sh
for i in {21..30} 
do
java -cp RadiusSimulator.jar -DUSERNAME=qa -DPASSWORD=Infoblox1492 -DRADIUS_SECRET=secret -DFRAMED_IP_ADDRESS=10.0.1."$i" -DFRAMED_IP_MASK=255.255.255.0 RadiusAccountingStart 10.36.141.15
sleep 5
java -cp RadiusSimulator.jar -DUSERNAME=qa -DPASSWORD=Infoblox1492 -DRADIUS_SECRET=secret -DFRAMED_IP_ADDRESS=1.2.3."$i" -DFRAMED_IP_MASK=255.255.255.0 RadiusAuthentication 10.36.141.15
sleep 5
done

#!/bin/sh
#
# This script is used to generate the sample certifications in this directory
# openssl and java keytool must be in the path
#

# genclientcert <root.crt> <root.key> <clientfilename> <clienturl>
function genclientcert {
  rootname=$1
  rootkey=$2
  certname=$3
  certurl=$4
  openssl genrsa -out $certname.key 1024
  openssl req -new -key $certname.key -out $certname.csr -subj "/C=US/ST=California/L=San Jose/O=Cisco Systems/OU=SAMPG/CN=$certurl/emailAddress=$certname@cisco.com"
  openssl x509 -req -sha256 -startdate -days 1826 -in $certname.csr -CA $rootname -CAkey $rootkey -set_serial 01 -out $certname.crt
  openssl pkcs12 -export -out $certname.p12 -inkey $certname.key -in $certname.crt -chain -CAfile $rootname -passin pass:cisco123 -passout pass:cisco123
  keytool -importkeystore -srckeystore $certname.p12 -destkeystore $certname.jks -srcstoretype PKCS12 -srcstorepass cisco123 -deststorepass cisco123
}

# genrootcert <rootname> <rooturl>
function genrootcert {
  certname=$1
  certurl=$2
  openssl genrsa -out $certname.key 1024
  openssl req -new -x509 -sha256 -days 1826 -key $certname.key -out $certname.crt -subj "/C=US/ST=California/L=San Jose/O=Cisco Systems/OU=SAMPG/CN=$certurl/emailAddress=$certname@cisco.com"
  openssl pkcs12 -export -out $certname.p12 -inkey $certname.key -in $certname.crt -passin pass:cisco123 -passout pass:cisco123
  keytool -importkeystore -srckeystore $certname.p12 -destkeystore $certname.jks -srcstoretype PKCS12 -srcstorepass cisco123 -deststorepass cisco123
}

genrootcert rootSample rootSample.cisco.com

for i in `seq 1 5`;
do
    genclientcert rootSample.crt rootSample.key clientSample$i clientSample$i.cisco.com
    genclientcert rootSample.crt rootSample.key iseSample$i iseSample$i.cisco.com
done

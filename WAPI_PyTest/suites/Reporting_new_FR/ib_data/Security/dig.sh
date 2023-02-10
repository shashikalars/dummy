#!/bin/sh
host=$1
echo $host
for (( i=1; i <= 50; i++ ))
do
dig @$host asm
done
for (( i=1; i <= 40; i++ ))
do
dig @$host asm1
done
for (( i=1; i <= 40; i++ ))
do
dig @$host g.com cname
done
for (( i=1; i <= 15; i++ ))
do
dig @$host blockdn.com
done



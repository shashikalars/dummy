#!/bin/bash

######################################################################
# Supported test items
######################################################################

#Negative tests covered so far:
#1.	"@" for attributes being removed from JSON: not supported according to dev (bug FIREYE-96)
#2.	Invalid "APT" name: all invalid forms reported correctly by syslog 
#3.	Invalid alert type in appliance/alert/@name: reported correctly by syslog
#4.	UTF chars in key/domain (IDN): not supported according to dev
#5.	Invalid alert severity: syslog reporting it correctly
#6.     Invalid text file as input to break system
#7.     Binary data as input to break system
#8.     Create special chars in values

#Positive tests covered
#1.     Single alert
#2.     Multiple alerts
#3.     Stress test: Multiple fireeye -> 1 NIOS
#4.     Multiple-alert per notification (except malware-object multiple-alert notification)

######################################################################
# To-be-supported test items
######################################################################
#(Done. Need to add a function) very large input json to break system
#(Done. Need to add a function) missing relevant fields
#(Done. Need to add a function) special SQL injection statement as value in fields

#Timestamp
#domain or ip etc (refer to Naveen's email)
#version of notification (6.0, 6.1, 6.2)
#json agnostic
#logging

######################################################################
# Test Execution
######################################################################
. ./generate_alert.sh

#Uncomment any test in the following section if you want to execute single alert test against malware-callback
#run_testcase_single_alert_malware-callback
#run_testcase_single_alert_malware-callback MY_ALERT_ID #Replace MY_ALERT_ID with your value
#Uncomment any test in the following section if you want to execute single alert test against malware-callback with APT
#run_testcase_single_alert_malware-callback_apt "Trojan.APT.DNS"
#run_testcase_single_alert_malware-callback_apt "APT.DNS"
#run_testcase_single_alert_malware-callback_apt "Trojan.APT"

#Uncomment any test in the following section if you want to execute single alert test against malware-object
#run_testcase_single_alert_malware-object
#run_testcase_single_alert_malware-object MY_ALERT_ID #Replace MY_ALERT_ID with your value
#Uncomment any test in the following section if you want to execute single alert test against malware-object with APT
#run_testcase_single_alert_malware-object_apt "Trojan.APT.DNS"
#run_testcase_single_alert_malware-object_apt "APT.DNS"
#run_testcase_single_alert_malware-object_apt "Trojan.APT"

#Uncomment any test in the following section if you want to execute single alert test against web-infection
#run_testcase_single_alert_web-infection
#run_testcase_single_alert_web-infection MY_ALERT_ID #Replace MY_ALERT_ID with your value
#Uncomment any test in the following section if you want to execute single alert test against web-infection with APT
#run_testcase_single_alert_web-infection_apt "Trojan.APT.DNS"
#run_testcase_single_alert_web-infection_apt "APT.DNS"
#run_testcase_single_alert_web-infection_apt "Trojan.APT"

#Uncomment any test in the following section if you want to execute single alert test against infection-match
#run_testcase_single_alert_infection-match
#run_testcase_single_alert_infection-match MY_ALERT_ID #Replace MY_ALERT_ID with your value
#Uncomment any test in the following section if you want to execute single alert test against infection-match with APT
#We currently don't have APT alert of infection-match type
##(N/A)run_testcase_single_alert_infection-match_apt "Trojan.APT.DNS"
##(N/A)run_testcase_single_alert_infection-match_apt "APT.DNS"
##(N/A)run_testcase_single_alert_infection-match_apt "Trojan.APT"

#Uncomment any test in the following section if you want to execute single alert test against domain-match
#run_testcase_single_alert_domain-match
#run_testcase_single_alert_domain-match MY_ALERT_ID #Replace MY_ALERT_ID with your value
#Uncomment any test in the following section if you want to execute single alert test against domain-match with APT
#run_testcase_single_alert_domain-match_apt "Trojan.APT.DNS"
#run_testcase_single_alert_domain-match_apt "APT.DNS"
#run_testcase_single_alert_domain-match_apt "Trojan.APT"

#Uncomment any test in the following section if you want to execute single alert test against all infection/alert type
run_testcase_single_alert_all
#run_testcase_single_alert_all_invalid
#run_testcase_single_alert_all_without_at_sign
#run_testcase_single_alert_all_invalid_severity

#Uncomment any test in the following section if you want to execute single alert with utf-8 values in key fields
#run_testcase_utf8_values_malware-callback

#Uncomment any test in the following section if you want to execute curl with a non-json input file
#run_testcase_invalid_json_txt_file
#run_testcase_invalid_json_binary_file

#Uncomment any test in the following section if you want to execute multiple alerts test against malware-callback
#run_testcase_multiple_alerts_malware-callback

#Uncomment any test in the following section if you want to execute multiple alerts test against malware-object
#run_testcase_multiple_alerts_malware-object

#Uncomment any test in the following section if you want to execute multiple alerts test against web-infection
#run_testcase_multiple_alerts_web-infection

#Uncomment any test in the following section if you want to execute multiple alerts test against infection-match
#run_testcase_multiple_alerts_infection-match

#Uncomment any test in the following section if you want to execute multiple alerts test against domain-match
#run_testcase_multiple_alerts_domain-match

#Uncomment any test in the following section if you want to execute multiple alerts test against all alert types
#run_testcase_multiple_alerts_all

#Uncomment any test in the following section if you want to execute stress test
#Concurrent tests currently have an issue of multiple tests competing with eacho other in writing test config file. Fixing it now...
#run_testcase_multiple_alerts_all_concurrent
#run_testcase_multiple_alerts_all_multipletimes
#run_testcase_multiple_alerts_all_concurrent_multipletimes



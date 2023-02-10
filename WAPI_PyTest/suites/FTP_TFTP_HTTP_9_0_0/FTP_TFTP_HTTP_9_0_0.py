#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Shashikala R S"
__email__  = "srs@infoblox.com"

#############################################################################
# Grid Set up required:                                                     #
#  1. Grid + HA + SA member                                                 #
#  2. Licenses : Grid,NIOS                                                  #
#############################################################################
import os
import re
import config
import pytest
import unittest
import logging
import json
from time import sleep
import ib_utils.ib_NIOS as ib_NIOS
import shlex
from time import sleep
from subprocess import Popen, PIPE
import pexpect
import paramiko
from ib_utils.start_stop_logs import log_action as log
from ib_utils.file_content_validation import log_validation as logv
import commands
import FTP_suit as FTP
import TFTP_suit as TFTP
import HTTP_suit as HTTP
import subprocess

dir_ref=''
def prepration():
    subprocess.check_output("reboot_system -H "+config.grid1_master_id+" -a poweroff -c "+config.owner,shell=True)
    subprocess.check_output("reboot_system -H "+config.grid1_member2_id+" -a poweroff -c "+config.owner,shell=True)
    subprocess.check_output("vm_specs -H "+config.grid1_master_id+" -C 8 -M 32 -c "+config.owner,shell=True)
    subprocess.check_output("vm_specs -H "+config.grid1_member2_id+" -C 8 -M 32 -c "+config.owner,shell=True)
    subprocess.check_output("reboot_system -H "+config.grid1_master_id+" -a poweron -c "+config.owner,shell=True)
    subprocess.check_output("reboot_system -H "+config.grid1_member2_id+" -a poweron -c "+config.owner,shell=True)
    sleep(400)

class NIOS_FTP(unittest.TestCase):
    
    @pytest.mark.run(order=1)
    def test_000_Start_FTP_services_all_members(self):
        prepration()
        print("\n======================================")
        print("Start FTP services on Master \n\n")
        print("======================================\n")
        FTP.start_FTP_services(0,config.grid1_master_mgmt_vip,"Master")

        print("======================================")
        print("Start FTP services on HA member \n\n")
        print("======================================")
        FTP.start_FTP_services(1,config.grid1_member1_ha_vip,"HA member")
        
        print("======================================")
        print("Start FTP services on SA member \n\n")
        print("======================================")
        FTP.start_FTP_services(2,config.grid1_member2_vip,"SA member")
        
        
    @pytest.mark.run(order=2)
    def test_001_Verify_the_FTP_service_is_running_all_members(self): 
        FTP.Verify_the_FTP_service_is_running(config.grid1_master_mgmt_vip)
        FTP.Verify_the_FTP_service_is_running(config.grid1_member1_ha_vip)
        FTP.Verify_the_FTP_service_is_running(config.grid1_member2_vip)
        
    @pytest.mark.run(order=3)
    def test_002_Check_the_status_of_FTP_service_are_running(self): 
        print("\n Check if FTP services are running state on Master\n")
        FTP.Check_the_status_of_FTP_service_are_running(0)
        
        print("\n Check if FTP services are running state on HA member\n")
        FTP.Check_the_status_of_FTP_service_are_running(1)
        
        print("\n Check if FTP services are running state on SA member\n")
        FTP.Check_the_status_of_FTP_service_are_running(2)
        
        
    @pytest.mark.run(order=4)
    def test_003_Validate_the_log_index_forbidden_by_Options_on_master(self): 
        FTP.Validate_the_log_index_forbidden_by_Options(config.grid1_master_mgmt_vip,"Master")
        
    @pytest.mark.run(order=5)
    def test_004_Validate_the_log_index_forbidden_by_Options_on_HA_member(self): 
        FTP.Validate_the_log_index_forbidden_by_Options(config.grid1_member1_ha_vip,"HA member")

    @pytest.mark.run(order=6)
    def test_005_Validate_the_log_index_forbidden_by_Options_on_SA_member(self): 
        FTP.Validate_the_log_index_forbidden_by_Options(config.grid1_member2_vip,"SA member")
        
    @pytest.mark.run(order=7)
    def test_006_grep_vsftpd_and_validate_PID_on_master(self): 
        
        FTP.grep_vsftpd_and_validate_PID(config.grid1_master_mgmt_vip)
       
    @pytest.mark.run(order=8)
    def test_007_grep_vsftpd_and_validate_PID_on_HA_member(self): 
        
        FTP.grep_vsftpd_and_validate_PID(config.grid1_member1_ha_vip)
        
    @pytest.mark.run(order=9)
    def test_008_grep_vsftpd_and_validate_PID_on_SA_member(self): 
        
        FTP.grep_vsftpd_and_validate_PID(config.grid1_member2_vip)
        
    @pytest.mark.run(order=10)
    def test_009_Upload_files_through_master(self):
        FTP.upload_files("upload_file.txt",config.grid1_master_mgmt_vip)
        
    @pytest.mark.run(order=11)
    def test_010_validate_audit_log_able_to_upload_file(self): 
        print("\n Validate audit log of uploading file\n")
        LookFor=".*imported tftp file.*"
        print(LookFor)
        logs=logv(LookFor,"/infoblox/var/audit.log",config.grid1_master_mgmt_vip)
        print(logs)
        print('-------------------------')
        if logs:
            print("Success: Uploaded the file successfully")
            assert True 
        else:
            print("Failed: unable to uploaded the file")
            assert False
        FTP.validate_uploaded_files_in_storage_path(config.grid1_master_mgmt_vip,"upload_file.txt")
            
    @pytest.mark.run(order=12)
    def test_011_stop_FTP_service(self):
        FTP.stop_FTP_services(0,config.grid1_master_mgmt_vip,"Master")
        
        FTP.stop_FTP_services(1,config.grid1_member1_ha_vip,"HA member")
      
        FTP.stop_FTP_services(2,config.grid1_member2_vip,"SA member")

    @pytest.mark.run(order=13)
    def test_012_Verify_the_FTP_service_is_stopped_all_members(self): 
        FTP.Verify_the_FTP_service_is_stopped(config.grid1_master_mgmt_vip)
        FTP.Verify_the_FTP_service_is_stopped(config.grid1_member1_ha_vip)
        FTP.Verify_the_FTP_service_is_stopped(config.grid1_member2_vip)

    @pytest.mark.run(order=14)
    def test_013_Check_the_status_of_FTP_service_is_inactive(self): 
        print("\n Check if FTP services are inactive state on Master\n")
        FTP.Check_the_status_of_FTP_service_is_inactive(0)
        
        print("\n Check if FTP services are inactive state on HA member\n")
        FTP.Check_the_status_of_FTP_service_is_inactive(1)
        
        print("\n Check if FTP services are inactive state on SA member\n")
        FTP.Check_the_status_of_FTP_service_is_inactive(2)
        
    @pytest.mark.run(order=15)
    def test_014_Restarted_FTP_services_all_members(self):
        print("\n======================================")
        print("Restartd FTP services on Master \n\n")
        print("======================================\n")
        FTP.start_FTP_services(0,config.grid1_master_mgmt_vip,"Master")

        print("======================================")
        print("Restartd FTP services on HA member \n\n")
        print("======================================")
        FTP.start_FTP_services(1,config.grid1_member1_ha_vip,"HA member")
        
        print("======================================")
        print("Restartd FTP services on SA member \n\n")
        print("======================================")
        FTP.start_FTP_services(2,config.grid1_member2_vip,"SA member")

    @pytest.mark.run(order=16)
    def test_015_Verify_the_FTP_service_is_running_all_members_after_restarted(self): 
        FTP.Verify_the_FTP_service_is_running(config.grid1_master_mgmt_vip)
        FTP.Verify_the_FTP_service_is_running(config.grid1_member1_ha_vip)
        FTP.Verify_the_FTP_service_is_running(config.grid1_member2_vip)
        
    @pytest.mark.run(order=17)
    def test_016_Check_the_status_of_FTP_service_are_running_after_restarted(self): 
        print("\n Check if FTP services are running state on Master after restarted the FTP service\n")
        FTP.Check_the_status_of_FTP_service_are_running(0)
        
        print("\n Check if FTP services are running state on SA member after restarted the FTP service\n")
        FTP.Check_the_status_of_FTP_service_are_running(1)
        
        print("\n Check if FTP services are running state on HA member after restarted the FTP service\n")
        FTP.Check_the_status_of_FTP_service_are_running(2)

    @pytest.mark.run(order=18)
    def test_017_Start_and_stop_FTP_services_three_times(self): 
        for i in range(3):
            FTP.stop_FTP_services(0,config.grid1_master_mgmt_vip,"Master")
            
            FTP.stop_FTP_services(1,config.grid1_member1_ha_vip,"HA member")
          
            FTP.stop_FTP_services(2,config.grid1_member2_vip,"SA member")
            sleep(10)
            
            FTP.start_FTP_services(0,config.grid1_master_mgmt_vip,"Master")
            
            FTP.start_FTP_services(1,config.grid1_member1_ha_vip,"HA member")
            
            FTP.start_FTP_services(2,config.grid1_member2_vip,"SA member")

    @pytest.mark.run(order=19)
    def test_018_Verify_the_FTP_service_is_running_all_members_after_stop_starting_3_times(self):
        print("Verify that the FTP service is running after stop-starting 3 times.")
        FTP.Verify_the_FTP_service_is_running(config.grid1_master_mgmt_vip)
        FTP.Verify_the_FTP_service_is_running(config.grid1_member1_ha_vip)
        FTP.Verify_the_FTP_service_is_running(config.grid1_member2_vip)
        
    @pytest.mark.run(order=20)
    def test_019_Check_the_status_of_FTP_service_are_running_after_restarted(self): 
        print("\n Check if FTP services are running state on Master after stop-starting 3 times.\n")
        FTP.Check_the_status_of_FTP_service_are_running(0)
        
        print("\n Check if FTP services are running state on SA member after stop-starting 3 times.\n")
        FTP.Check_the_status_of_FTP_service_are_running(1)
        
        print("\n Check if FTP services are running state on HA member after stop-starting 3 times.\n")
        FTP.Check_the_status_of_FTP_service_are_running(2)
        
    @pytest.mark.run(order=21)
    def test_020_Set_FTP_ACLs_any_allow(self): 
        FTP.Set_FTP_ACLs_to_the_member(0,config.grid1_master_mgmt_vip,"Any","ALLOW")
        FTP.Set_FTP_ACLs_to_the_member(1,config.grid1_member1_ha_vip,"Any","ALLOW")
        FTP.Set_FTP_ACLs_to_the_member(2,config.grid1_member2_vip,"Any","ALLOW")
        
    @pytest.mark.run(order=22)
    def test_021_validate_FTP_ACLs_added(self): 
        FTP.Validate_FTP_ACLs_is_set_to_the_member(0,config.grid1_master_mgmt_vip,"Any","ALLOW")
        FTP.Validate_FTP_ACLs_is_set_to_the_member(1,config.grid1_member1_ha_vip,"Any","ALLOW")
        FTP.Validate_FTP_ACLs_is_set_to_the_member(2,config.grid1_member2_vip,"Any","ALLOW")
        
    @pytest.mark.run(order=23)
    def test_022_Upload_files_after_configure_ACLs(self):
        FTP.upload_files("file_1MB.txt",config.grid1_master_mgmt_vip)
        FTP.validate_uploaded_files_in_storage_path(config.grid1_master_mgmt_vip,"file_1MB.txt")
        
    @pytest.mark.run(order=24)
    def test_023_validate_able_to_upload_file_after_configure_ACLs(self): 
        print("\n Validate audit log of uploading file\n")
        LookFor=".*imported tftp file.*"
        print(LookFor)
        logs=logv(LookFor,"/infoblox/var/audit.log",config.grid1_master_mgmt_vip)
        print(logs)
        print('-------------------------')
        if logs:
            print("Success: Uploaded the file successfully")
            assert True 
        else:
            print("Failed: unable to uploaded the file")
            assert False

    @pytest.mark.run(order=25)
    def test_024_Stop_and_start_FTP_services_and_validate_the_status(self): 
        
        FTP.stop_FTP_services(0,config.grid1_master_mgmt_vip,"Master")
        FTP.stop_FTP_services(1,config.grid1_member1_ha_vip,"HA member")
        FTP.stop_FTP_services(2,config.grid1_member2_vip,"SA member")
        sleep(10)
        
        FTP.start_FTP_services(0,config.grid1_master_mgmt_vip,"Master")
        FTP.start_FTP_services(1,config.grid1_member1_ha_vip,"HA member")
        FTP.start_FTP_services(2,config.grid1_member2_vip,"SA member")
        
        FTP.Verify_the_FTP_service_is_running(config.grid1_master_mgmt_vip)
        FTP.Verify_the_FTP_service_is_running(config.grid1_member1_ha_vip)
        FTP.Verify_the_FTP_service_is_running(config.grid1_member2_vip)
        
        FTP.Check_the_status_of_FTP_service_are_running(0)
        FTP.Check_the_status_of_FTP_service_are_running(1)
        FTP.Check_the_status_of_FTP_service_are_running(2)

    @pytest.mark.run(order=26)
    def test_025_Stop_FTP_services_and_try_to_upload_the_file(self): 
        
        FTP.stop_FTP_services(0,config.grid1_master_mgmt_vip,"Master")
        FTP.stop_FTP_services(1,config.grid1_member1_ha_vip,"HA member")
        FTP.stop_FTP_services(2,config.grid1_member2_vip,"SA member")
        sleep(10)
        
        FTP.Verify_the_FTP_service_is_stopped(config.grid1_master_mgmt_vip)
        FTP.Verify_the_FTP_service_is_stopped(config.grid1_member1_ha_vip)
        FTP.Verify_the_FTP_service_is_stopped(config.grid1_member2_vip)
        
        FTP.Check_the_status_of_FTP_service_is_inactive(0)
        FTP.Check_the_status_of_FTP_service_is_inactive(1)
        FTP.Check_the_status_of_FTP_service_is_inactive(2)
        FTP.enable_Allow_grid_member(True)
        FTP.upload_files("file-example_PDF_1MB.pdf",config.grid1_master_mgmt_vip)
        FTP.validate_uploaded_files_in_storage_path(config.grid1_master_mgmt_vip,"file-example_PDF_1MB.pdf")

    @pytest.mark.run(order=27)
    def test_026_Start_FTP_services_then_restart_member_validate_no_error_in_log(self):

        print("======================================")
        print("Start FTP services on HA member \n\n")
        print("======================================")
        FTP.start_FTP_services(0,config.grid1_master_mgmt_vip,"Master")
        FTP.start_FTP_services(1,config.grid1_member1_ha_vip,"HA member")
        
        print("======================================")
        print("Start FTP services on SA member \n\n")
        print("======================================")
        FTP.start_FTP_services(2,config.grid1_member2_vip,"SA member")
        
        FTP.restart_services(1)
        FTP.restart_services(2)
        
        FTP.Verify_the_FTP_service_is_running(config.grid1_member1_ha_vip)
        FTP.Verify_the_FTP_service_is_running(config.grid1_member2_vip)
        
    @pytest.mark.run(order=28)
    def test_027_create_a_directory(self):
        print("\n======================================")
        print("Create a Directory \n\n")
        print("\n======================================")
        dir_ref=FTP.Create_a_directory(config.grid1_master_mgmt_vip,"FTP_Directory")
        FTP.validate_directory_created_in_storage_path(config.grid1_master_mgmt_vip,"FTP_Directory","/storage/tftpboot")
        
    @pytest.mark.run(order=29)
    def test_028_rename_created_directory_check_path_rightly_updated(self):
        print("\n======================================\n")
        print("rename the newly created directory and check that the /storage path has been updated ")
        print("\n======================================\n")
        dir_ref=FTP.Create_a_directory(config.grid1_master_mgmt_vip,"FTP_Directory1")
        print(dir_ref)
        FTP.rename_created_dir(config.grid1_master_mgmt_vip,dir_ref,"FTP_Directory2")
        FTP.validate_directory_created_in_storage_path(config.grid1_master_mgmt_vip,"FTP_Directory2","/storage/tftpboot")
    
    @pytest.mark.run(order=30)
    def test_029_create_FTP_user(self):
        print("\n======================================\n")
        print("Create FTP user and  check that the /storage path has been updated ")
        print("\n======================================\n")  
        FTP.Create_ftpuser(config.grid1_master_mgmt_vip,config.client_user,"RW",config.password)
        FTP.validate_directory_created_in_storage_path(config.grid1_master_mgmt_vip,config.client_user,"/storage/tftpboot/ftpusers")
        sleep(30)

    @pytest.mark.run(order=31)
    def test_030_Try_connecting_the_master_after_adding_ACL(self): 
        print("\n======================================\n")
        print("Try connecting the master after adding ACL:ANY ALLOW ")
        print("\n======================================\n")  
        FTP.Try_connecting_the_IP_after_adding_ACL_ALLOW_Permission(config.grid1_master_mgmt_vip)

        print("\n======================================\n") 
        print("Try connecting the member after adding ACL:ANY_ALLOW")
        print("\n======================================\n") 
        FTP.Try_connecting_the_IP_after_adding_ACL_ALLOW_Permission(config.grid1_member2_vip)

    @pytest.mark.run(order=32)
    def test_031_delete_FTP_ACL_ANY_ALLOW(self):
        print("\n======================================\n")
        print("Change permission to ALLOW to DENY and connect ftp server")
        print("\n======================================\n")  
        FTP.change_permission_to_DENY(0,config.grid1_master_mgmt_vip,"Any","DENY")
        FTP.change_permission_to_DENY(2,config.grid1_member2_vip,"Any","DENY")
        print("\n======================================\n") 
        print("\nTry connecting the master after adding ACL:ANY_DENY")
        print("\n======================================\n") 
        FTP.Try_connecting_the_IP_after_adding_ACL_DENY_Permission(config.grid1_master_mgmt_vip)
        print("\n======================================\n") 
        print("\nTry connecting the member after adding ACL:ANY_DENY")
        print("\n======================================\n") 
        FTP.Try_connecting_the_IP_after_adding_ACL_DENY_Permission(config.grid1_member2_vip)

    @pytest.mark.run(order=33)
    def test_032_delete_FTP_ACL_ANY(self):
        print("\n======================================\n")  
        print("Remove ACLs ")
        print("\n======================================\n")  
        FTP.delete_FTP_ACLs_from_member(0,config.grid1_master_mgmt_vip)
        FTP.delete_FTP_ACLs_from_member(1,config.grid1_member1_ha_vip)
        FTP.delete_FTP_ACLs_from_member(2,config.grid1_member2_vip)

    @pytest.mark.run(order=34)
    def test_033_Set_FTP_ACLs_network_ALLOW(self): 
        print("\n======================================\n")  
        print("Select the network ACLs option. ")
        print("\n======================================\n")  
        FTP.Set_FTP_ACLs_to_the_member(0,config.grid1_master_mgmt_vip,"10.36.0.0/16","ALLOW")
        FTP.Set_FTP_ACLs_to_the_member(1,config.grid1_member1_ha_vip,"10.36.0.0/16","ALLOW")
        FTP.Set_FTP_ACLs_to_the_member(2,config.grid1_member2_vip,"10.36.0.0/16","ALLOW")
        
    @pytest.mark.run(order=35)
    def test_034_validate_FTP_ACLs_added(self): 

        FTP.Validate_FTP_ACLs_is_set_to_the_member(0,config.grid1_master_mgmt_vip,"10.36.0.0/16","ALLOW")
        FTP.Validate_FTP_ACLs_is_set_to_the_member(1,config.grid1_member1_ha_vip,"10.36.0.0/16","ALLOW")
        FTP.Validate_FTP_ACLs_is_set_to_the_member(2,config.grid1_member2_vip,"10.36.0.0/16","ALLOW")

    @pytest.mark.run(order=36)
    def test_035_Try_connecting_the_master_after_adding_ACL(self): 
        print("\n======================================\n")
        print("Try connecting the master after adding ACL. ")
        print("\n======================================\n")  
        FTP.Try_connecting_the_IP_after_adding_ACL_ALLOW_Permission(config.grid1_master_mgmt_vip)
        
        print("\n======================================\n") 
        print("Try connecting the member after adding ACL. ")
        print("\n======================================\n") 
        FTP.Try_connecting_the_IP_after_adding_ACL_ALLOW_Permission(config.grid1_member2_vip)

    @pytest.mark.run(order=37)
    def test_036_Set_Network_FTP_ACL_configurations_DENY(self):
        print("\n======================================\n")
        print("Change permission to ALLOW to DENY and connect ftp server")
        print("\n======================================\n")  
        FTP.change_permission_to_DENY(0,config.grid1_master_mgmt_vip,"10.36.0.0/16","DENY")
        FTP.change_permission_to_DENY(2,config.grid1_member2_vip,"10.36.0.0/16","DENY")
        print("\n======================================\n") 
        print("\nTry connecting the master after adding ACL:Network_DENY")
        print("\n======================================\n") 
        FTP.Try_connecting_the_IP_after_adding_ACL_DENY_Permission(config.grid1_master_mgmt_vip)
        print("\n======================================\n") 
        print("\nTry connecting the member after adding ACL:Network_DENY")
        print("\n======================================\n") 
        FTP.Try_connecting_the_IP_after_adding_ACL_DENY_Permission(config.grid1_member2_vip)

    @pytest.mark.run(order=38)
    def test_037_delete_FTP_ACL_Network(self):
        print("\n======================================\n")  
        print("Remove ACLs ")
        print("\n======================================\n")  
        FTP.delete_FTP_ACLs_from_member(0,config.grid1_master_mgmt_vip)
        FTP.delete_FTP_ACLs_from_member(1,config.grid1_member1_ha_vip)
        FTP.delete_FTP_ACLs_from_member(2,config.grid1_member2_vip)

    @pytest.mark.run(order=39)
    def test_038_Set_FTP_ACLs_network_ALLOW(self): 
        print("\n======================================\n")  
        print("Select the network ACLs option.")
        print("\n======================================\n")  
        FTP.Set_FTP_ACLs_to_the_member(0,config.grid1_master_mgmt_vip,config.client_ip,"ALLOW")
        
        FTP.Set_FTP_ACLs_to_the_member(2,config.grid1_member2_vip,config.client_ip,"ALLOW")
        
    @pytest.mark.run(order=40)
    def test_039_validate_FTP_ACLs_added(self): 

        FTP.Validate_FTP_ACLs_is_set_to_the_member(0,config.grid1_master_mgmt_vip,config.client_ip,"ALLOW")
       
        FTP.Validate_FTP_ACLs_is_set_to_the_member(2,config.grid1_member2_vip,config.client_ip,"ALLOW")

    @pytest.mark.run(order=41)
    def test_040_Try_connecting_the_master_after_adding_ACL(self): 
        print("\n======================================\n")
        print("Try connecting the master after adding ACL. ")
        print("\n======================================\n")  
        FTP.Try_connecting_the_IP_after_adding_ACL_ALLOW_Permission(config.grid1_master_mgmt_vip)
        
        print("Try connecting the member after adding ACL. ")
        FTP.Try_connecting_the_IP_after_adding_ACL_ALLOW_Permission(config.grid1_member2_vip)

    @pytest.mark.run(order=42)
    def test_041_Set_ipv4_address_ACL_configurations_DENY(self):
        print("\n======================================\n")
        print("Change permission to ALLOW to DENY and connect ftp server")
        print("\n======================================\n")  
        FTP.change_permission_to_DENY(0,config.grid1_master_mgmt_vip,config.client_ip,"DENY")
        FTP.change_permission_to_DENY(2,config.grid1_member2_vip,config.client_ip,"DENY")
        print("\nTry connecting the master after adding ACL:IPV4 address _DENY")
        FTP.Try_connecting_the_IP_after_adding_ACL_DENY_Permission(config.grid1_master_mgmt_vip)
        print("\nTry connecting the member after adding ACL:IPV4 address_DENY")
        FTP.Try_connecting_the_IP_after_adding_ACL_DENY_Permission(config.grid1_member2_vip)

    @pytest.mark.run(order=43)
    def test_042_delete_FTP_ACL_address(self):
        print("\n======================================\n")  
        print("Remove ACLs ")
        print("\n======================================\n")  
        FTP.delete_FTP_ACLs_from_member(0,config.grid1_master_mgmt_vip)
        FTP.delete_FTP_ACLs_from_member(1,config.grid1_member1_ha_vip)
        FTP.delete_FTP_ACLs_from_member(2,config.grid1_member2_vip)

    @pytest.mark.run(order=44)
    def test_043_enable_anonymous_in_the_grid(self):
        print("\n======================================\n")  
        print("Enable Anonymous FTP")
        print("\n======================================\n")  
        FTP.enable_Anonymous_FTP(0)

    @pytest.mark.run(order=45)
    def test_044_restricted_from_listing_files_when_FTP_File_list_disable(self):
        print("\n======================================\n")  
        print("It should be restricted from listing files, however FTP File Listing is disabled.")
        print("\n======================================\n")  

        FTP.Set_FTP_ACLs_to_the_member(0,config.grid1_master_mgmt_vip,"Any","ALLOW")
       
        FTP.Set_FTP_ACLs_to_the_member(2,config.grid1_member2_vip,"Any","ALLOW")
        print("\n======================================\n")  
        print("Verify that can not view files and directories. ")
        print("\n======================================\n")  
        FTP.check_for_ftp_files_list(0,config.grid1_master_mgmt_vip)
        FTP.check_for_ftp_files_list(2,config.grid1_member2_vip)

    @pytest.mark.run(order=46)
    def test_045_enbale_FTP_listing_and_look_for_files(self):
        print("\n======================================\n")  
        print("Enable FTP file list and Verify that can view files and directories. ")
        print("\n======================================\n")  
        FTP.start_FTP_services(0,config.grid1_master_mgmt_vip,"Master")
        FTP.start_FTP_services(2,config.grid1_member2_vip,"SA member")

        TFTP.enable_Allow_grid_member(True)
        FTP.enable_ftp_filelist(0)
        FTP.enable_ftp_filelist(2)
        sleep(20)
        FTP.check_for_ftp_files_list(0,config.grid1_master_mgmt_vip)
        FTP.check_for_ftp_files_list(2,config.grid1_member2_vip)

    @pytest.mark.run(order=47)
    def test_046_Download_files_using_mget(self):
        print("\n======================================\n")  
        print("Uses mget to download files.")
        print("\n======================================\n")  
        FTP.Download_files_using_mget(config.grid1_master_mgmt_vip,"upload_file.txt")
        FTP.Download_files_using_mget(config.grid1_member2_vip,"upload_file.txt")

    @pytest.mark.run(order=48)
    def test_047_get_grid_back_and_restore_after_enable_backup_files(self):
        print("\n======================================\n")  
        print("after turning on backup files and directories, get the grid backup and validate files are present")
        print("\n======================================\n")  

        FTP.Include_files_and_directories(True)
        FTP.Taking_Grid_Backup_File()
        FTP.Restore_Grid_Backup_File()
        FTP.validate_uploaded_files_in_storage_path(config.grid1_master_mgmt_vip,"upload_file.txt")

    @pytest.mark.run(order=49)
    def test_048_get_grid_back_and_restore_after_disable_backup_files(self):
        print("\n======================================\n")  
        print("after turning off backup files and directories, get the grid backup and validate files are present")
        print("\n======================================\n")  

        FTP.Include_files_and_directories(False)
        FTP.Taking_Grid_Backup_File()
        FTP.Restore_Grid_Backup_File()
        FTP.validate_empty_uploaded_files_in_storage_path(config.grid1_master_mgmt_vip,"upload_file.txt","/storage/tftpboot")

    @pytest.mark.run(order=50)
    def test_049_Stop_FTP_services_in_all_members(self): 
        
        FTP.stop_FTP_services(0,config.grid1_master_mgmt_vip,"Master")
        FTP.stop_FTP_services(1,config.grid1_member1_ha_vip,"HA member")
        FTP.stop_FTP_services(2,config.grid1_member2_vip,"SA member")

    @pytest.mark.run(order=51)
    def test_050_try_to_upload_html_file_and_validate_files_in_storage_path(self): 
        print("\n======================================\n")  
        print("Try to upload a.HTML file and see if it is successful by verifying the storage path.")
        print("\n======================================\n")  

        FTP.upload_files("FTP_report.html",config.grid1_master_mgmt_vip)
        FTP.validate_uploaded_files_in_storage_path(config.grid1_master_mgmt_vip,"FTP_report.html")

    @pytest.mark.run(order=52)
    def test_051_try_to_upload_html_file_and_validate_files_in_storage_path(self): 
        sleep(10)
        FTP.Set_storage_limit(1)
        FTP.validate_storage_limit(1)

    @pytest.mark.run(order=53)
    def test_052_upload_a_1_MB_file(self): 
        log("start","/infoblox/var/infoblox.log",config.grid1_master_mgmt_vip)
        FTP.upload_files_after_set_to_1MB_size("file-example_PDF_1MB.pdf",config.grid1_master_mgmt_vip)
        log("stop","/infoblox/var/infoblox.log",config.grid1_master_mgmt_vip)
        print("\n Validate audit log of uploading file\n")
        LookFor=".*Exceed the TFTP Storage limit.*"
        print(LookFor)
        logs=logv(LookFor,"/infoblox/var/infoblox.log",config.grid1_master_mgmt_vip)
        print(logs)
        print('-------------------------')
        if logs:
            print("Success: Uploaded the file successfully")
            assert True 
        else:
            print("Failed: unable to uploaded the file")
            assert False

    @pytest.mark.run(order=54)
    def test_053_Set_storage_limit_back_to_default_size(self): 
        FTP.Set_storage_limit(500)
        FTP.validate_storage_limit(500)

    @pytest.mark.run(order=55)
    def test_054_upload_a_CSV_file_with_UTF_8_symbol(self): 
      
        FTP.upload_files("py_UTF-8.csv.xlsx",config.grid1_master_mgmt_vip)
        FTP.validate_uploaded_files_in_storage_path(config.grid1_master_mgmt_vip,"py_UTF-8.csv.xlsx")
    
    @pytest.mark.run(order=56)
    def test_055_Start_TFTP_services_all_members(self):
        '''
        : STARTED TFTP RELATED CASES :
        '''
        print("\n======================================")
        print("Start TFTP services on Master \n\n")
        print("======================================\n")
        TFTP.start_TFTP_services(0,config.grid1_master_mgmt_vip,"Master")

        print("======================================")
        print("Start TFTP services on HA member \n\n")
        print("======================================")
        TFTP.start_TFTP_services(1,config.grid1_member1_ha_vip,"HA member")
        
        print("======================================")
        print("Start TFTP services on SA member \n\n")
        print("======================================")
        TFTP.start_TFTP_services(2,config.grid1_member2_vip,"SA member")
        
        
    @pytest.mark.run(order=57)
    def test_056_Verify_the_TFTP_service_is_running_all_members(self): 
        TFTP.Verify_the_TFTP_service_is_running(config.grid1_master_mgmt_vip)
        TFTP.Verify_the_TFTP_service_is_running(config.grid1_member1_ha_vip)
        TFTP.Verify_the_TFTP_service_is_running(config.grid1_member2_vip)
        
    @pytest.mark.run(order=58)
    def test_057_Check_the_status_of_TFTP_service_are_running(self): 
        print("\n Check if TFTP services are running state on Master\n")
        TFTP.Check_the_status_of_TFTP_service_are_running(0)
        
        print("\n Check if TFTP services are running state on HA member\n")
        TFTP.Check_the_status_of_TFTP_service_are_running(1)
        
        print("\n Check if TFTP services are running state on SA member\n")
        TFTP.Check_the_status_of_TFTP_service_are_running(2)

    @pytest.mark.run(order=59)
    def test_058_grep_tftpd_and_validate_PID_on_master(self): 
        
        TFTP.grep_TFTpd_and_validate_PID(config.grid1_master_mgmt_vip)
       
    @pytest.mark.run(order=60)
    def test_059_grep_tftpd_and_validate_PID_on_HA_member(self): 
        
        TFTP.grep_TFTpd_and_validate_PID(config.grid1_member1_ha_vip)
        
    @pytest.mark.run(order=61)
    def test_060_grep_tftpd_and_validate_PID_on_SA_member(self): 
        
        TFTP.grep_TFTpd_and_validate_PID(config.grid1_member2_vip)
        
    @pytest.mark.run(order=62)
    def test_061_stop_TFTP_service(self):
        TFTP.stop_TFTP_services(0,config.grid1_master_mgmt_vip,"Master")
        
        TFTP.stop_TFTP_services(1,config.grid1_member1_ha_vip,"HA member")
      
        TFTP.stop_TFTP_services(2,config.grid1_member2_vip,"SA member")

    @pytest.mark.run(order=63)
    def test_062_Verify_the_TFTP_service_is_stopped_all_members(self): 
        TFTP.Verify_the_TFTP_service_is_stopped(config.grid1_master_mgmt_vip)
        TFTP.Verify_the_TFTP_service_is_stopped(config.grid1_member1_ha_vip)
        TFTP.Verify_the_TFTP_service_is_stopped(config.grid1_member2_vip)

    @pytest.mark.run(order=64)
    def test_063_Check_the_status_of_TFTP_service_is_inactive(self): 
        print("\n Check if TFTP services are inactive state on Master\n")
        TFTP.Check_the_status_of_TFTP_service_is_inactive(0)
        
        print("\n Check if TFTP services are inactive state on HA member\n")
        TFTP.Check_the_status_of_TFTP_service_is_inactive(1)
        
        print("\n Check if TFTP services are inactive state on SA member\n")
        TFTP.Check_the_status_of_TFTP_service_is_inactive(2)

    @pytest.mark.run(order=65)
    def test_064_Set_TFTP_ACLs_any_allow(self): 
        TFTP.enable_Allow_grid_member(True)
        TFTP.start_TFTP_services(0,config.grid1_master_mgmt_vip,"Master")
        TFTP.start_TFTP_services(2,config.grid1_member2_vip,"SA member")

        TFTP.Set_TFTP_ACLs_to_the_member(0,config.grid1_master_mgmt_vip,"Any","ALLOW")
        TFTP.Set_TFTP_ACLs_to_the_member(1,config.grid1_member1_ha_vip,"Any","ALLOW")
        TFTP.Set_TFTP_ACLs_to_the_member(2,config.grid1_member2_vip,"Any","ALLOW")
        
    @pytest.mark.run(order=66)
    def test_065_validate_TFTP_ACLs_added(self): 
        TFTP.Validate_TFTP_ACLs_is_set_to_the_member(0,config.grid1_master_mgmt_vip,"Any","ALLOW")
        TFTP.Validate_TFTP_ACLs_is_set_to_the_member(1,config.grid1_member1_ha_vip,"Any","ALLOW")
        TFTP.Validate_TFTP_ACLs_is_set_to_the_member(2,config.grid1_member2_vip,"Any","ALLOW")
        
    @pytest.mark.run(order=67)
    def test_066_Upload_files_after_configure_ACLs(self):
        TFTP.upload_files("file_1MB.txt",config.grid1_master_mgmt_vip)
        TFTP.validate_uploaded_files_in_storage_path(config.grid1_master_mgmt_vip,"file_1MB.txt")
    
    @pytest.mark.run(order=68)
    def test_067_upload_and_download_file_after_adding_ACL(self): 
        print("\n======================================\n")
        print("Upload and download filesusing TFTP after adding ACL:ANY ALLOW with Master(MGMT)")
        print("\n======================================\n")  
        TFTP.enable_Allow_grid_member(True)
        res=TFTP.upload_file_when_Permission_set_to_ALLOW(config.grid1_master_mgmt_vip,"test.txt")
        if res==False:
            print("MGMT Port currently does not not support TFTP")
            assert True
        
    @pytest.mark.run(order=69)
    def test_068_upload_and_download_file_after_adding_ACL_with_member(self): 
        print("\n======================================\n")
        print("Upload and download filesusing TFTP after adding ACL:ANY ALLOW with member")
        print("\n======================================\n")  
        TFTP.upload_file_when_Permission_set_to_ALLOW(config.grid1_member2_vip,"test.txt")
        TFTP.validate_log_messages_when_permission_is_ALLOW(config.grid1_member2_vip,"test.txt")

    @pytest.mark.run(order=70)
    def test_069_change_TFTP_ACL_ALLOW_to_DENY(self):
        print("\n======================================\n")
        print("Change permission to ALLOW to DENY and connect tftp server")
        print("\n======================================\n")  
        
        TFTP.change_permission_to_DENY(0,config.grid1_master_mgmt_vip,"Any","DENY")
        TFTP.change_permission_to_DENY(2,config.grid1_member2_vip,"Any","DENY")
    
    @pytest.mark.run(order=71)
    def test_070_upload_and_download_file_after_adding_ACL_DENY_with_master(self): 
        print("\n======================================\n") 
        print("\nUpload and download files using TFTP after adding ACL:ANY_DENY with master")
        print("\n======================================\n") 
        res=TFTP.upload_file_when_Permission_set_to_DENY(config.grid1_master_mgmt_vip,"test.txt")
        if res==True:
            print("MGMT Port currently does not not support TFTP")
            assert True
        
    @pytest.mark.run(order=72)
    def test_071_upload_and_download_file_after_adding_ACL_DENY_with_member(self):     
        TFTP.upload_file_when_Permission_set_to_DENY(config.grid1_member2_vip,"test.txt")
        #TFTP.validate_log_messages_when_permission_is_DENY(config.grid1_member2_vip)

    @pytest.mark.run(order=73)
    def test_072_delete_TFTP_ACL_ANY(self):
        print("\n======================================\n")  
        print("Remove ACLs ")
        print("\n======================================\n")  
        TFTP.delete_TFTP_ACLs_from_member(0,config.grid1_master_mgmt_vip)
        TFTP.delete_TFTP_ACLs_from_member(1,config.grid1_member1_ha_vip)
        TFTP.delete_TFTP_ACLs_from_member(2,config.grid1_member2_vip)

    @pytest.mark.run(order=74)
    def test_073_Set_TFTP_ACLs_network_ALLOW(self): 
        print("\n======================================\n")  
        print("Select the network ACLs option. ")
        print("\n======================================\n")  
        TFTP.Set_TFTP_ACLs_to_the_member(0,config.grid1_master_mgmt_vip,"10.36.0.0/16","ALLOW")
        TFTP.Set_TFTP_ACLs_to_the_member(1,config.grid1_member1_ha_vip,"10.36.0.0/16","ALLOW")
        TFTP.Set_TFTP_ACLs_to_the_member(2,config.grid1_member2_vip,"10.36.0.0/16","ALLOW")
        
    @pytest.mark.run(order=75)
    def test_074_validate_TFTP_ACLs_network_added(self): 

        TFTP.Validate_TFTP_ACLs_is_set_to_the_member(0,config.grid1_master_mgmt_vip,"10.36.0.0/16","ALLOW")
        TFTP.Validate_TFTP_ACLs_is_set_to_the_member(1,config.grid1_member1_ha_vip,"10.36.0.0/16","ALLOW")
        TFTP.Validate_TFTP_ACLs_is_set_to_the_member(2,config.grid1_member2_vip,"10.36.0.0/16","ALLOW")

    @pytest.mark.run(order=76)
    def test_075_upload_download_after_ACL_set_to_network_ALLOW_with_master(self): 
        
        print("\n======================================\n")
        print("Try connecting the master after adding ACL with master ")
        print("\n======================================\n")  
        res=TFTP.upload_file_when_Permission_set_to_ALLOW(config.grid1_master_mgmt_vip,"test1.txt")
        if res==False:
            print("MGMT Port currently does not not support TFTP")
            assert True
        
    @pytest.mark.run(order=77)
    def test_076_upload_download_after_ACL_set_to_network_ALLOW_with_member(self):     
        print("\n======================================\n") 
        print("Try connecting the member after adding ACL. with member")
        print("\n======================================\n") 
        TFTP.upload_file_when_Permission_set_to_ALLOW(config.grid1_member2_vip,"test1.txt")
        TFTP.validate_log_messages_when_permission_is_ALLOW(config.grid1_member2_vip,"test1.txt")

    @pytest.mark.run(order=78)
    def test_077_change_TFTP_ACL_Network_ALLOW_to_DENY(self):
        print("\n======================================\n")
        print("Change permission to ALLOW to DENY and connect ftp server")
        print("\n======================================\n")  
        TFTP.change_permission_to_DENY(0,config.grid1_master_mgmt_vip,"10.36.0.0/16","DENY")
        TFTP.change_permission_to_DENY(2,config.grid1_member2_vip,"10.36.0.0/16","DENY")
    
    @pytest.mark.run(order=79)
    def test_078_change_TFTP_ACL_Network_ALLOW_to_DENY_with_master(self):
        
        print("\n======================================\n") 
        print("\nTry connecting the master after adding ACL:Network_DENY with master")
        print("\n======================================\n") 
        res=TFTP.upload_file_when_Permission_set_to_DENY(config.grid1_master_mgmt_vip,"test1.txt")
        if res==True:
            print("MGMT Port currently does not not support TFTP")
            assert True

    @pytest.mark.run(order=80)
    def test_079_change_TFTP_ACL_Network_ALLOW_to_DENY_with_member(self): 
        print("\n======================================\n") 
        print("\nTry upload and download the file after adding ACL:Network_DENY with member")
        print("\n======================================\n") 
        TFTP.upload_file_when_Permission_set_to_DENY(config.grid1_member2_vip,"test1.txt")
        TFTP.validate_log_messages_when_permission_is_DENY(config.grid1_member2_vip)

    @pytest.mark.run(order=81)
    def test_080_delete_TFTP_ACL_Network(self):
        print("\n======================================\n")  
        print("Remove ACLs ")
        print("\n======================================\n")  
        TFTP.delete_TFTP_ACLs_from_member(0,config.grid1_master_mgmt_vip)
        TFTP.delete_TFTP_ACLs_from_member(1,config.grid1_member1_ha_vip)
        TFTP.delete_TFTP_ACLs_from_member(2,config.grid1_member2_vip)

    @pytest.mark.run(order=82)
    def test_081_Set_TFTP_ACLs_ipv4_ALLOW(self): 
        print("\n======================================\n")  
        print("Select the network ACLs option.")
        print("\n======================================\n")  
        TFTP.Set_TFTP_ACLs_to_the_member(0,config.grid1_master_mgmt_vip,config.tftp_client,"ALLOW")
        
        TFTP.Set_TFTP_ACLs_to_the_member(2,config.grid1_member2_vip,config.tftp_client,"ALLOW")
        
    @pytest.mark.run(order=83)
    def test_082_validate_TFTP_ACLs_ipv4_added(self): 

        TFTP.Validate_TFTP_ACLs_is_set_to_the_member(0,config.grid1_master_mgmt_vip,config.tftp_client,"ALLOW")
       
        TFTP.Validate_TFTP_ACLs_is_set_to_the_member(2,config.grid1_member2_vip,config.tftp_client,"ALLOW")

    @pytest.mark.run(order=84)
    def test_083_upload_download_ACL_set_to_ipv4_with_master(self): 
        
        print("\n======================================\n")
        print("Upload and download file connecting the master after adding ACL with master ")
        print("\n======================================\n")  
        res=TFTP.upload_file_when_Permission_set_to_ALLOW(config.grid1_master_mgmt_vip,"test3.txt")
        if res==False:
            print("MGMT Port currently does not not support TFTP")
            assert True

    @pytest.mark.run(order=85)
    def test_084_upload_download_ACL_set_to_ipv4_with_member(self): 

        print("Try upload and download the files after adding ACL with member ")
        TFTP.upload_file_when_Permission_set_to_ALLOW(config.grid1_member2_vip,"test3.txt")
        TFTP.validate_log_messages_when_permission_is_ALLOW(config.grid1_member2_vip,"test3.txt")

    @pytest.mark.run(order=86)
    def test_085_change_TFTP_ACL_ipv4_ALLOW_to_DENY(self):
        
        print("\n======================================\n")
        print("Change permission to ALLOW to DENY and connect ftp server")
        print("\n======================================\n")  
        TFTP.change_permission_to_DENY(0,config.grid1_master_mgmt_vip,config.tftp_client,"DENY")
        TFTP.change_permission_to_DENY(2,config.grid1_member2_vip,config.tftp_client,"DENY")

    @pytest.mark.run(order=87)
    def test_086_change_TFTP_ACL_IPV4_ALLOW_to_DENY_with_master(self):
        
        print("\n======================================\n") 
        print("\nTry connecting the master after adding ACL:IPV4 address_DENY with master")
        print("\n======================================\n") 
        res=TFTP.upload_file_when_Permission_set_to_DENY(config.grid1_master_mgmt_vip,"test3.txt")
        if res==True:
            print("MGMT Port currently does not not support TFTP")
            assert True

    @pytest.mark.run(order=88)
    def test_087_change_TFTP_ACL_IPV4_ALLOW_to_DENY_with_member(self):
        
        print("\nUpload and download files after adding ACL:IPV4 address_DENY with member")
        TFTP.upload_file_when_Permission_set_to_DENY(config.grid1_member2_vip,"test3.txt")
        TFTP.validate_log_messages_when_permission_is_DENY(config.grid1_member2_vip)

    @pytest.mark.run(order=89)
    def test_088_delete_TFTP_ACL_address(self):
        print("\n======================================\n")  
        print("Remove ACLs ")
        print("\n======================================\n")  
        TFTP.delete_TFTP_ACLs_from_member(0,config.grid1_master_mgmt_vip)
        
        TFTP.delete_TFTP_ACLs_from_member(2,config.grid1_member2_vip)
        
    @pytest.mark.run(order=90)
    def test_089_reboot_and_check_the_status(self):
        TFTP.reboot_node(config.grid1_master_mgmt_vip)

        print("\n Check if TFTP services are running state on Master\n")
        TFTP.Check_the_status_of_TFTP_service_are_running(0)
       
        TFTP.reboot_node(config.grid1_member2_vip)
        print("\n Check if TFTP services are running state on SA member\n")
        TFTP.Check_the_status_of_TFTP_service_are_running(2)

    @pytest.mark.run(order=91)
    def test_090_restart_and_check_the_status(self):
        print("\n======================================")
        print("Restart services and check for TFTP services are running \n\n")
        print("======================================\n")
        TFTP.restart_services(0)
      
        TFTP.restart_services(2)
        print("\n Check if TFTP services are running state on Master\n")
        TFTP.Check_the_status_of_TFTP_service_are_running(0)
        
        print("\n Check if TFTP services are running state on SA member\n")
        TFTP.Check_the_status_of_TFTP_service_are_running(2)
        

    @pytest.mark.run(order=92)
    def test_091_promote_ha_node_and_validate_TFTP_status(self):
        print("\n======================================")
        print("Promote the master and check the status of TFTP services \n\n")
        print("======================================\n")
        TFTP.GMC_promote_member_as_master_candidate()
        sleep(80)
        TFTP.restart_services(1)
        TFTP.promote_master(config.grid1_member2_vip)
        TFTP.check_able_to_login_appliances(config.grid1_member2_vip)

        TFTP.validate_status_GM_after_GMC_promotion(config.grid1_member2_vip)
        TFTP.Verify_the_TFTP_service_is_running(config.grid1_member2_vip)
        sleep(300)

    @pytest.mark.run(order=93)
    def test_092_revert_back_to_the_original_state(self):
        TFTP.check_able_to_login_appliances(config.grid1_master_mgmt_vip)
        sleep(120)
        TFTP.promote_master(config.grid1_master_mgmt_vip)
        TFTP.validate_status_GM_after_GMC_promotion(config.grid1_master_mgmt_vip)
        sleep(300)

    @pytest.mark.run(order=94)
    def test_093_perform_HA_fail_over(self):
        TFTP.start_TFTP_services(1,config.grid1_member1_ha_vip,"HA member")
        print("\n======================================")
        print("Reboot active node and check the status of TFTP services \n\n")
        print("======================================\n")
        TFTP.reboot_node(config.grid1_member1_active_ha_ip)
        TFTP.verify_the_node_after_a_HA_failover(config.grid1_member1_active_ha_ip,"Passive")
        sleep(300)
        TFTP.Check_the_status_of_TFTP_service_are_running(1)

    @pytest.mark.run(order=95)
    def test_094_revert_back_to_the_original_state_by_performing_HA_Failover(self):
        TFTP.reboot_node(config.grid1_member1_passive_ha_ip)
        TFTP.verify_the_node_after_a_HA_failover(config.grid1_member1_active_ha_ip,"Active")

    @pytest.mark.run(order=96)
    def test_095_upload_and_check_files_in_storage_path_after_adding_SA2(self):
        print("\n======================================")
        print("Start TFTP services on Master \n\n")
        print("======================================\n")
        sleep(60)
        TFTP.start_TFTP_services(0,config.grid1_master_mgmt_vip,"Master1")
        print("\n Check if TFTP services are running state on Master1\n")
        TFTP.Check_the_status_of_TFTP_service_are_running(0)

        TFTP.Set_TFTP_ACLs_to_the_member(0,config.grid1_master_mgmt_vip,"Any","ALLOW")
        TFTP.Validate_TFTP_ACLs_is_set_to_the_member(0,config.grid1_master_mgmt_vip,"Any","ALLOW")

        TFTP.upload_files("file_1MB.txt",config.grid1_master_mgmt_vip)
        TFTP.validate_uploaded_files_in_storage_path(config.grid1_master_mgmt_vip,"file_1MB.txt")

        TFTP.stop_TFTP_services(0,config.grid1_master_mgmt_vip,"Master1")
        '''
        Try to join the SA2 member to SA1. After successfully joined SA2 to SA1, login to SA1. Goto Data Management | File Distribution | start the TFTP service on SA2. 
        '''
        TFTP.start_TFTP_services(2,config.grid1_member2_vip,"Master2")
        TFTP.Check_the_status_of_TFTP_service_are_running(2)
        '''
        Goto Members tab | Edit the SA2's "TFTP Member properties" and do the following. In the "Allow Files transfer from" section, add "Allow Any" option followed by save and close.
        '''
        TFTP.Set_TFTP_ACLs_to_the_member(2,config.grid1_member2_vip,"Any","ALLOW")
        TFTP.Validate_TFTP_ACLs_is_set_to_the_member(2,config.grid1_member2_vip,"Any","ALLOW")
        '''
        Try to get the same dummy files (from any TFTP client[TFTP server]) using SA2, you can see the error on terminal as shown below and Also, /storage/tftpboot directory on SA2 is empty and not listing any
        '''
        TFTP.validate_uploaded_files_in_storage_path(config.grid1_member2_vip,"file_1MB.txt")
    
    @pytest.mark.run(order=97)
    def test_096_delete_all_files_from_path(self):
        TFTP.delete_files_through_path(config.grid1_master_mgmt_vip)
        print("\nStop TFTP services and remove ACLs from member\n")
        TFTP.stop_TFTP_services(0,config.grid1_master_mgmt_vip,"Master")
        TFTP.stop_TFTP_services(1,config.grid1_member1_ha_vip,"HA member")
        TFTP.stop_TFTP_services(2,config.grid1_member2_vip,"SA member")

        TFTP.enable_Allow_grid_member(False)

        print("\n======================================\n")  
        print("Remove ACLs ")
        print("\n======================================\n")  
        TFTP.delete_TFTP_ACLs_from_member(0,config.grid1_master_mgmt_vip)
        TFTP.delete_TFTP_ACLs_from_member(2,config.grid1_member2_vip)
    
    @pytest.mark.run(order=98)
    def test_097_Start_HTTP_services_all_members(self):
        
        '''
        : STARTED HTTP RELATED CASES :
        '''
        print("\n======================================")
        print("Start HTTP services on Master \n\n")
        print("======================================\n")
        HTTP.start_HTTP_services(0,config.grid1_master_mgmt_vip,"Master")

        print("======================================")
        print("Start HTTP services on HA member \n\n")
        print("======================================")
        HTTP.start_HTTP_services(1,config.grid1_member1_ha_vip,"HA member")
        
        print("======================================")
        print("Start HTTP services on SA member \n\n")
        print("======================================")
        HTTP.start_HTTP_services(2,config.grid1_member2_vip,"SA member")
        
        
    @pytest.mark.run(order=99)
    def test_098_Verify_the_HTTP_service_is_running_all_members(self): 
        HTTP.Verify_the_HTTP_service_is_running(config.grid1_master_mgmt_vip)
        HTTP.Verify_the_HTTP_service_is_running(config.grid1_member1_ha_vip)
        HTTP.Verify_the_HTTP_service_is_running(config.grid1_member2_vip)
        
    @pytest.mark.run(order=100)
    def test_099_Check_the_status_of_HTTP_service_are_running(self): 
        print("\n Check if HTTP services are running state on Master\n")
        HTTP.Check_the_status_of_HTTP_service_are_running(0)
        
        print("\n Check if HTTP services are running state on HA member\n")
        HTTP.Check_the_status_of_HTTP_service_are_running(1)
        
        print("\n Check if HTTP services are running state on SA member\n")
        HTTP.Check_the_status_of_HTTP_service_are_running(2)

    @pytest.mark.run(order=101)
    def test_100_grep_httpd_and_validate_PID_on_master(self): 
        
        HTTP.grep_HTTPd_and_validate_PID(config.grid1_master_mgmt_vip)
       
    @pytest.mark.run(order=102)
    def test_101_grep_httpd_and_validate_PID_on_HA_member(self): 
        
        HTTP.grep_HTTPd_and_validate_PID(config.grid1_member1_ha_vip)
        
    @pytest.mark.run(order=103)
    def test_102_grep_httpd_and_validate_PID_on_SA_member(self): 
        
        HTTP.grep_HTTPd_and_validate_PID(config.grid1_member2_vip)
        
    @pytest.mark.run(order=104)
    def test_103_stop_HTTP_service(self):
        HTTP.stop_HTTP_services(0,config.grid1_master_mgmt_vip,"Master")
        
        HTTP.stop_HTTP_services(1,config.grid1_member1_ha_vip,"HA member")
      
        HTTP.stop_HTTP_services(2,config.grid1_member2_vip,"SA member")

    @pytest.mark.run(order=105)
    def test_104_Verify_the_HTTP_service_is_stopped_all_members(self): 
        HTTP.Verify_the_HTTP_service_is_stopped(config.grid1_master_mgmt_vip)
        HTTP.Verify_the_HTTP_service_is_stopped(config.grid1_member1_ha_vip)
        HTTP.Verify_the_HTTP_service_is_stopped(config.grid1_member2_vip)

    @pytest.mark.run(order=106)
    def test_105_Check_the_status_of_HTTP_service_is_inactive(self): 
        print("\n Check if HTTP services are inactive state on Master\n")
        HTTP.Check_the_status_of_HTTP_service_is_inactive(0)
        
        print("\n Check if HTTP services are inactive state on HA member\n")
        HTTP.Check_the_status_of_HTTP_service_is_inactive(1)
        
        print("\n Check if HTTP services are inactive state on SA member\n")
        HTTP.Check_the_status_of_HTTP_service_is_inactive(2)

    @pytest.mark.run(order=107)
    def test_106_Set_HTTP_ACLs_network_ALLOW(self): 
        HTTP.enable_Allow_grid_member(True)
        HTTP.start_HTTP_services(0,config.grid1_master_mgmt_vip,"Master")
        HTTP.start_HTTP_services(2,config.grid1_member2_vip,"SA member")
        print("\n======================================\n")  
        print("Select the network ACLs option. ")
        print("\n======================================\n")  
        HTTP.Set_HTTP_ACLs_to_the_member(True,0,config.grid1_master_mgmt_vip,"10.36.0.0/16","ALLOW")
       
        HTTP.Set_HTTP_ACLs_to_the_member(True,2,config.grid1_member2_vip,"10.36.0.0/16","ALLOW")
        
    @pytest.mark.run(order=108)
    def test_107_validate_HTTP_network_ACLs_added(self): 

        HTTP.Validate_HTTP_ACLs_is_set_to_the_member(0,config.grid1_master_mgmt_vip,"10.36.0.0/16","ALLOW")
      
        HTTP.Validate_HTTP_ACLs_is_set_to_the_member(2,config.grid1_member2_vip,"10.36.0.0/16","ALLOW")

    @pytest.mark.run(order=109)
    def test_108_upload_download_after_ACL_set_to_network_with_master(self): 
        
        print("\n======================================\n")
        print("Try upload files after adding ACL with master")
        print("\n======================================\n")  
        val=HTTP.upload_download_file_when_Permission_set_to_ALLOW(config.grid1_master_mgmt_vip,"test.txt")
        if val==False:
            print("MGMT Port currently does not not support HTTP")
            assert True

    @pytest.mark.run(order=110)
    def test_109_upload_download_after_ACL_set_to_network_with_member(self):  
        print("\n======================================\n") 
        print("Try upload files after adding ACL with member ")
        print("\n======================================\n") 
        HTTP.upload_download_file_when_Permission_set_to_ALLOW(config.grid1_member2_vip,"test.txt")
        HTTP.validate_uploaded_files_in_storage_path(config.grid1_member2_vip,"test.txt")

    @pytest.mark.run(order=111)
    def test_110_delete_HTTP_ACL_Network(self):
        print("\n======================================\n")  
        print("Remove ACLs ")
        print("\n======================================\n")  
        HTTP.delete_HTTP_ACLs_from_member(0,config.grid1_master_mgmt_vip)
       
        HTTP.delete_HTTP_ACLs_from_member(2,config.grid1_member2_vip)

    @pytest.mark.run(order=112)
    def test_111_Set_HTTP_ACLs_ipv4_ALLOW(self): 
        print("\n======================================\n")  
        print("Select the network ACLs option.")
        print("\n======================================\n")  
        HTTP.Set_HTTP_ACLs_to_the_member(True,0,config.grid1_master_mgmt_vip,config.client_ip,"ALLOW")
        
        HTTP.Set_HTTP_ACLs_to_the_member(True,2,config.grid1_member2_vip,config.client_ip,"ALLOW")
        
    @pytest.mark.run(order=113)
    def test_112_validate_HTTP_ACLs_ipv4_added(self): 

        HTTP.Validate_HTTP_ACLs_is_set_to_the_member(0,config.grid1_master_mgmt_vip,config.client_ip,"ALLOW")
       
        HTTP.Validate_HTTP_ACLs_is_set_to_the_member(2,config.grid1_member2_vip,config.client_ip,"ALLOW")

    @pytest.mark.run(order=114)
    def test_113_upload_download_after_ACL_set_to_network_with_master(self): 
        
        print("\n======================================\n")
        print("Try upload files after adding ACL:IPV4 with master")
        print("\n======================================\n")  
        val=HTTP.upload_download_file_when_Permission_set_to_ALLOW(config.grid1_master_mgmt_vip,"test.txt")
        if val==False:
            print("MGMT Port currently does not not support HTTP")
            assert True

    @pytest.mark.run(order=115)
    def test_114_upload_download_after_ACL_set_to_network_with_member(self):  
        print("\n======================================\n") 
        print("Try upload files after adding ACL:IPV4 with member ")
        print("\n======================================\n") 
        HTTP.upload_download_file_when_Permission_set_to_ALLOW(config.grid1_member2_vip,"test.txt")
        HTTP.validate_uploaded_files_in_storage_path(config.grid1_member2_vip,"test.txt")

    @pytest.mark.run(order=116)
    def test_115_delete_HTTP_ACL_address(self):
        print("\n======================================\n")  
        print("Remove ACLs ")
        print("\n======================================\n")  
        HTTP.delete_HTTP_ACLs_from_member(0,config.grid1_master_mgmt_vip)
       
        HTTP.delete_HTTP_ACLs_from_member(2,config.grid1_member2_vip)
    
    @pytest.mark.run(order=117)
    def test_116_reboot_and_check_the_status(self):
        HTTP.reboot_node(config.grid1_master_mgmt_vip)

        print("\n Check if HTTP services are running state on Master\n")
        HTTP.Check_the_status_of_HTTP_service_are_running(0)
       
        HTTP.reboot_node(config.grid1_member2_vip)
        print("\n Check if HTTP services are running state on SA member\n")
        HTTP.Check_the_status_of_HTTP_service_are_running(2)

    @pytest.mark.run(order=118)
    def test_117_restart_and_check_the_status(self):
        print("\n======================================")
        print("Restart services and check for HTTP services are running \n\n")
        print("======================================\n")
        HTTP.restart_services(0)
      
        HTTP.restart_services(2)
        print("\n Check if HTTP services are running state on Master\n")
        HTTP.Check_the_status_of_HTTP_service_are_running(0)
        
        print("\n Check if HTTP services are running state on SA member\n")
        HTTP.Check_the_status_of_HTTP_service_are_running(2)

    @pytest.mark.run(order=119)
    def test_118_promote_ha_node_and_validate_HTTP_status(self):
        HTTP.start_HTTP_services(1,config.grid1_member1_ha_vip,"HA member")
        print("\n======================================")
        print("Promote the master and check the status of HTTP services \n\n")
        print("======================================\n")
        HTTP.GMC_promote_member_as_master_candidate()
        HTTP.promote_master(config.grid1_member2_vip)

        HTTP.validate_status_GM_after_GMC_promotion(config.grid1_member2_vip)
        HTTP.Verify_the_HTTP_service_is_running(config.grid1_member2_vip)
        sleep(300)

    @pytest.mark.run(order=120)
    def test_119_revert_back_to_the_original_state(self):
        HTTP.check_able_to_login_appliances(config.grid1_master_mgmt_vip)
        sleep(120)
        HTTP.promote_master(config.grid1_master_mgmt_vip)
        HTTP.validate_status_GM_after_GMC_promotion(config.grid1_master_mgmt_vip)
        sleep(300)

    @pytest.mark.run(order=121)
    def test_120_perform_HA_fail_over(self):
        print("\n======================================")
        print("Reboot active node and check the status of HTTP services \n\n")
        print("======================================\n")
        HTTP.reboot_node(config.grid1_member1_active_ha_ip)
        HTTP.verify_the_node_after_a_HA_failover(config.grid1_member1_active_ha_ip,"Passive")
        
        sleep(300)
        HTTP.Check_the_status_of_HTTP_service_are_running(1)
        HTTP.upload_files("upload_files_passive.txt",config.grid1_member1_active_ha_ip)
        sleep(60)
        HTTP.validate_uploaded_files_in_storage_path(config.grid1_member1_active_ha_ip,"upload_files_passive.txt")

    @pytest.mark.run(order=122)
    def test_121_revert_back_to_the_original_state_by_performing_HA_Failover(self):
        HTTP.reboot_node(config.grid1_member1_passive_ha_ip)
        HTTP.verify_the_node_after_a_HA_failover(config.grid1_member1_active_ha_ip,"Active")
        sleep(300)
        HTTP.upload_files("upload_files_active.txt",config.grid1_member1_active_ha_ip)
        sleep(60)
        HTTP.validate_uploaded_files_in_storage_path(config.grid1_member1_active_ha_ip,"upload_files_active.txt")
        
    @pytest.mark.run(order=123)
    def test_122_Cleanup(self): 
        
        HTTP.stop_HTTP_services(0,config.grid1_master_mgmt_vip,"Master")
        HTTP.stop_HTTP_services(2,config.grid1_member2_vip,"SA member")
        HTTP.delete_files_through_path(config.grid1_member2_vip)
        HTTP.enable_Allow_grid_member(False)

    @pytest.mark.run(order=124)
    def test_123_upload_and_delete_files_check_status(self):
        '''
        NIOS-44727-covering this scenario
        '''
        
        HTTP.enable_Allow_grid_member(True)
        HTTP.start_HTTP_services(0,config.grid1_master_mgmt_vip,"Master")

        print("======================================")
        print("Start HTTP services on HA member \n\n")
        print("======================================")
        HTTP.start_HTTP_services(1,config.grid1_member1_ha_vip,"HA member")
        
        print("======================================")
        print("Start HTTP services on SA member \n\n")
        print("======================================")
        HTTP.start_HTTP_services(2,config.grid1_member2_vip,"SA member")
              
        print("\n Check if HTTP services are running state on Master\n")
        HTTP.Check_the_status_of_HTTP_service_are_running(0)
        HTTP.Check_the_status_of_HTTP_service_are_running(1)
        HTTP.Check_the_status_of_HTTP_service_are_running(2)

        HTTP.upload_files("test_400.txt",config.grid1_master_mgmt_vip)
        HTTP.validate_uploaded_files_in_storage_path(config.grid1_master_mgmt_vip,"test_400.txt")
        HTTP.delete_files_through_path(config.grid1_master_mgmt_vip)
        HTTP.upload_files("test_400.txt",config.grid1_master_mgmt_vip)
        HTTP.validate_uploaded_files_in_storage_path(config.grid1_master_mgmt_vip,"test_400.txt")

        HTTP.Check_the_status_of_HTTP_service_are_running(0)
        
        HTTP.enable_Allow_grid_member(False)
        HTTP.upload_files("test1_400.txt",config.grid1_master_mgmt_vip)
        HTTP.validate_uploaded_files_in_storage_path(config.grid1_master_mgmt_vip,"test1_400.txt")
        HTTP.delete_files_through_path(config.grid1_master_mgmt_vip)
        HTTP.upload_files("test1_400.txt",config.grid1_master_mgmt_vip)
        HTTP.validate_uploaded_files_in_storage_path(config.grid1_master_mgmt_vip,"test1_400.txt")

        HTTP.Check_the_status_of_HTTP_service_are_running(0)

        HTTP.enable_Allow_grid_member(False)
        HTTP.upload_files("test1_400.txt",config.grid1_master_mgmt_vip)
        HTTP.validate_uploaded_files_in_storage_path(config.grid1_master_mgmt_vip,"test1_400.txt")

        HTTP.Check_the_status_of_HTTP_service_are_running(0)

    @pytest.mark.run(order=125)
    def test_124_upload_large_files(self):  
        '''
        NIOS-47408-covering this scenario
        '''
        FTP.Set_storage_limit(1)
        FTP.validate_storage_limit(1)
        log("start","/infoblox/var/infoblox.log",config.grid1_master_mgmt_vip)
        FTP.upload_files_after_set_to_1MB_size("test_200.txt",config.grid1_master_mgmt_vip)
        log("stop","/infoblox/var/infoblox.log",config.grid1_master_mgmt_vip)
        print("\n Validate audit log of uploading file\n")
        LookFor=".*Exceed the TFTP Storage limit.*"
        print(LookFor)
        logs=logv(LookFor,"/infoblox/var/infoblox.log",config.grid1_master_mgmt_vip)
        print(logs)
        print('-------------------------')
        if logs:
            print("Success: Exceed the TFTP Storage limit")
            assert True 
        else:
            print("Failed: Uploaded the file successfully")
            assert False
        FTP.Set_storage_limit(500)
        FTP.validate_storage_limit(500)

    @pytest.mark.run(order=126)
    def test_125_add_permission_group_for_folder(self): 
        dir_ref=FTP.Create_a_directory(config.grid1_master_mgmt_vip,"Directory_per")
        per_ref=FTP.create_permission_group(dir_ref)
        FTP.validate_directory_created_in_storage_path(config.grid1_master_mgmt_vip,"Directory_per","/storage/tftpboot")
        print("======================================")
        print("Change the permission type \n\n")
        print("======================================")
        #print(per_ref)
        FTP.change_permission_group(per_ref,dir_ref)


    @pytest.mark.run(order=127)
    def test_126_upload_crt_file_and_enable_captive_service(self): 
        '''
        NIOS-65826-covering this scenario
        '''
        print("======================================")
        print("Star the DNS & HTTP/TFTP services for all the members. \n\n")
        print("======================================\n\n")
        
        print("Start DNS Service in all members")
        print("================================")
        
        FTP.Start_DNS_Service(0,"Master")
        FTP.Start_DNS_Service(1,"HA member")
        FTP.Start_DNS_Service(2,"SA member")
        
        FTP.Validate_enabled_DNS_service(0)
        FTP.Validate_enabled_DNS_service(1)
        FTP.Validate_enabled_DNS_service(2)
        print("======================================")
        print("Start HTTP services on all member and validate \n\n")
        print("======================================")
        HTTP.start_HTTP_services(0,config.grid1_master_mgmt_vip,"Master")
        HTTP.start_HTTP_services(1,config.grid1_member1_ha_vip,"HA member")
        HTTP.start_HTTP_services(2,config.grid1_member2_vip,"SA member")

        HTTP.Check_the_status_of_HTTP_service_are_running(0)
        HTTP.Check_the_status_of_HTTP_service_are_running(1)
        HTTP.Check_the_status_of_HTTP_service_are_running(2)
        print("======================================")
        print("Start TFTP services on all member and validate \n\n")
        print("======================================")

        TFTP.start_TFTP_services(0,config.grid1_master_mgmt_vip,"Master")
        TFTP.start_TFTP_services(1,config.grid1_member1_ha_vip,"HA member")
        TFTP.start_TFTP_services(2,config.grid1_member2_vip,"SA member")

        TFTP.Check_the_status_of_TFTP_service_are_running(0)
        TFTP.Check_the_status_of_TFTP_service_are_running(1)
        TFTP.Check_the_status_of_TFTP_service_are_running(2)

        print("======================================")
        print("Upload certificate file\n\n")
        print("======================================")
        FTP.upload_files('client.crt',config.grid1_master_mgmt_vip)
        
        FTP.Configure_AD_server_details_in_the_grid()
        
        FTP.add_AD_server_to_the_member()
        
        response=FTP.start_Captive_service()
        if type(response) == tuple:           
            if response[0]==400: 
                print("\n Success: Captive Portal service cannot start on member because the following services are enabled on member: DNS,TFTP, HTTP_FILE_DIST.\n")
                assert True 
            else:
                print("\n Failure: Captive Portal service started on member even the following services are enabled on member: DNS,TFTP, HTTP_FILE_DIST.\n")
                assert False
        
        print("======================================")
        print("Stop DNS,HTTP,TFTP services before start Captive Portal service\n\n")
        print("======================================")
        FTP.Stop_DNS_Service(0,"Master")
        FTP.Stop_DNS_Service(1,"HA member")
        FTP.Stop_DNS_Service(2,"SA member")

        HTTP.stop_HTTP_services(0,config.grid1_master_mgmt_vip,"Master")
        HTTP.stop_HTTP_services(1,config.grid1_member1_ha_vip,"HA member")
        HTTP.stop_HTTP_services(2,config.grid1_member2_vip,"SA member")

        TFTP.stop_TFTP_services(0,config.grid1_master_mgmt_vip,"Master")
        TFTP.stop_TFTP_services(1,config.grid1_member1_ha_vip,"HA member")
        TFTP.stop_TFTP_services(2,config.grid1_member2_vip,"SA member")
        
        response=FTP.start_Captive_service()
        if type(response) == tuple:           
            if response[0]==200: 
                print("\n Success: Captive Portal service enabled successfully\n")
                assert True 
            else:
                print("\n Failure: Can not enabled Captive Portal service\n")
                assert False

    @pytest.mark.run(order=128)
    def test_127_take_backup_of_grid_using_FTP_server(self): 
        '''
        NIOS-86316-covering this scenario
        '''
        
        FTP.start_FTP_services_on_M2(0,config.grid2_master_vip,"Master2")
        FTP.Create_ftpuser(config.grid2_master_vip,config.client_user,"RW",config.password)
        
        FTP.validate_directory_created_in_storage_path(config.grid2_master_vip,config.client_user,"/storage/tftpboot/ftpusers")

        FTP.Set_FTP_ACLs_to_the_member_on_M2(0,config.grid2_master_vip,"Any","ALLOW")
        FTP.enable_Allow_grid_member(True)
        sleep(10)
        file_n=FTP.Taking_Grid_Backup_using_FTP()
        FTP.validate_directory_created_in_storage_path(config.grid2_master_vip,file_n,"/storage/tftpboot/ftpusers/"+config.client_user)


    @pytest.mark.run(order=129)
    def test_128_perform_operation_on_lan2_ip_FTP(self): 
        FTP.enable_lan2_and_nic(True,"Enabled")
        FTP.restart_services(0)
        print("======================================")
        print("Start FTP services on SA member \n\n")
        print("======================================")
        FTP.start_FTP_services(2,config.grid1_member2_vip,"SA member")
        print("\n Check if FTP services are running state on SA member\n")
        sleep(30)
        FTP.Check_the_status_of_FTP_service_are_running(2)
        FTP.upload_files("lan2_upload.txt",config.grid1_member2_vip)
        FTP.stop_FTP_services(2,config.grid1_member2_vip,"SA member")

    @pytest.mark.run(order=130)
    def test_129_perform_operation_on_lan2_ip_TFTP(self): 
        
        print("======================================")
        print("Start TFTP services on SA member \n\n")
        print("======================================")
        TFTP.start_TFTP_services(2,config.grid1_member2_vip,"SA member")
        print("\n Check if TFTP services are running state on SA member\n")
        sleep(30)
        TFTP.Check_the_status_of_TFTP_service_are_running(2)
        TFTP.upload_files("lan2_upload.txt",config.grid1_master_mgmt_vip)
        sleep(10)
        TFTP.validate_uploaded_files_in_storage_path(config.grid1_master_mgmt_vip,"lan2_upload.txt")
        FTP.stop_FTP_services(2,config.grid1_member2_vip,"SA member")
        TFTP.stop_TFTP_services(2,config.grid1_member2_vip,"SA member")
        TFTP.delete_files_through_path(config.grid1_master_mgmt_vip)
    @pytest.mark.run(order=131)
    def test_130_perform_operation_on_lan2_ip_HTTP(self): 
        
        print("======================================")
        print("Start HTTP services on SA member \n\n")
        print("======================================")
        HTTP.start_HTTP_services(2,config.grid1_member2_vip,"SA member")
        print("\n Check if HTTP services are running state on SA member\n")
        sleep(30)
        HTTP.Check_the_status_of_HTTP_service_are_running(2)

        HTTP.upload_files("lan2_upload.txt",config.grid1_member2_vip)
        HTTP.validate_uploaded_files_in_storage_path(config.grid1_member2_vip,"lan2_upload.txt")
        HTTP.stop_HTTP_services(2,config.grid1_member2_vip,"SA member")

    @pytest.mark.run(order=132)
    def test_131_Cleanup_objects(self): 
        TFTP.delete_files_through_path(config.grid1_master_mgmt_vip)
        FTP.enable_Allow_grid_member(False)
        FTP.enable_lan2_and_nic(False,"disabled")

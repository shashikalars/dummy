__author__ = "Aditya G"
__email__  = "adityag@infoblox.com"

########################################################################################
#  Grid Set up required:                                                               #
#  1. SA Grid Master                                                                   #
#  2. Licenses : DNS, DHCP, Grid, NIOS (IB-V1425), RPZ                                 #
########################################################################################


import config
import pytest
import unittest
import logging
import json
import os
import re
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.common_utilities as ib_TOKEN
from time import sleep
import pexpect


logging.basicConfig(filename='niosspt78412.log', filemode='w', level=logging.DEBUG)

def display_msg(msg):
    print(msg)
    logging.info(msg)

def import_csv(filename,update_method):
    display_msg("Starting csv import")
    
    dir_name = os.getcwd()+'/NIOS-78412/'
    base_filename = filename
    
    token =ib_TOKEN.generate_token_from_file(dir_name, base_filename)
    display_msg("---------TOKEN GENERATED---------------------")
    display_msg(token)
    display_msg("---------------------------------------------")
    data = {"token": token,"action":"START", "doimport":True, "on_error":"STOP","update_method":update_method}
    response = ib_NIOS.wapi_request('POST', object_type="fileop", fields=json.dumps(data),params="?_function=csv_import")
    display_msg("-----------------CSV IMPORT DETAILS------------------")
    display_msg("logging response")
    display_msg(response)
    display_msg("--------------------------------------------------------------------")
    response=json.loads(response)
    sleep(10)
    
    data={"action":"START","file_name":filename,"on_error":"CONTINUE","operation":"CREATE","separator":"COMMA"}
    get_ref=ib_NIOS.wapi_request('GET', object_type="csvimporttask")
    display_msg("-----------------FETCHING STATUS OF CSV IMPORTS FOR VERIFICATION -----------------")
    display_msg(get_ref)
    display_msg("----------------------------------------------------------------------------------")
    get_ref=json.loads(get_ref)
    
    for ref in get_ref:
        if response["csv_import_task"]["import_id"]==ref["import_id"]:
            if ref["lines_failed"]==0:
                raise Exception("CSV import successful, CSV import should have been unsuccessful due to missing required fields")
            else:
                display_msg("CSV import unsuccessful, CSV import failed as the required fields are empty")


def restart_services():
    logging.info("Restart services")
    grid =  ib_NIOS.wapi_request('GET', object_type="grid")
    ref = json.loads(grid)[0]['_ref']
    publish={"member_order":"SIMULTANEOUSLY"}
    request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
    sleep(5)


class NIOSSPT_78412(unittest.TestCase):

    @pytest.mark.run(order=1)
    def test_001_Change_hostname_of_the_grid_master(self):
        display_msg("**********************************************")
        display_msg("*              Testcase 01                   *")
        display_msg("**********************************************")
        display_msg("Fetching grid master reference")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member")
        master_ref=''
        for ref in json.loads(get_ref):
            if ref['host_name'] == config.grid_fqdn:
                master_ref = ref['_ref']
                display_msg(master_ref)
                break
        if master_ref == '':
            display_msg("Reference of master grid not found")
            assert False
        display_msg("Changing the hostname of master grid to infoblox.localdomain")
        data = {"host_name": "infoblox.localdomain"}
        response = ib_NIOS.wapi_request('PUT', ref=master_ref, fields=json.dumps(data))
        if bool(re.match("\"member*.",str(response))):
            display_msg("Hostname of master changed successfully")
            sleep(180)
            assert True
        else:
            display_msg("Changing hostname of the master failed")
            assert False


    @pytest.mark.run(order=2)
    def test_002_Enable_recursion_and_start_DNS_service(self):
        
        display_msg("**********************************************")
        display_msg("*              Testcase 02                   *")
        display_msg("**********************************************")
        display_msg("-------Start DNS service-------")
        
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns")
        display_msg("Member DNS reference")
        display_msg(get_ref)
        member_dns_ref = json.loads(get_ref)[0]['_ref']
        data = {"enable_dns": True}
        response = ib_NIOS.wapi_request('PUT', ref=member_dns_ref, fields=json.dumps(data))
        display_msg("Enable DNS, request response")
        if bool(re.match("\"member:dns*.",str(response))):
            display_msg("DNS service started successfully")
            sleep(20)
            assert True
        else:
            display_msg("Starting DNS service failed")
            assert False

        
        display_msg("-------Enabling recursion on Grid DNS-------")

        display_msg("Fetch Grid DNS reference")
        get_grid_dns_ref = ib_NIOS.wapi_request('GET', object_type='grid:dns')
        display_msg("Grid DNS reference is given below")
        display_msg(get_grid_dns_ref)
        grid_dns_ref = json.loads(get_grid_dns_ref)[0]['_ref']
        data = {"allow_recursive_query": True}
        response = ib_NIOS.wapi_request('PUT', ref=grid_dns_ref, fields=json.dumps(data))
        display_msg("Response for enable recursion on Grid DNS")
        display_msg(response)
        if bool(re.match("\"grid:dns*.",str(response))):
            display_msg("Recursion enabled successfully")
            restart_services()
            assert True
        else:
            display_msg("Enabling recursion on the grid failed")
            assert False


    @pytest.mark.run(order=3)
    def test_003_Import_RPZ_Substitute_Zone_With_Missing_Mandatory_Fields(self):
        
        display_msg("**********************************************")
        display_msg("*              Testcase 03                   *")
        display_msg("**********************************************")
        display_msg("Import CSV file for RPZ Substitute Zone with missing mandatory field substitute_name")
        import_csv("test_003_import_rpz_substitute_zone_with_missing_fields.csv","OVERRIDE")
        restart_services()

    @pytest.mark.run(order=4)
    def test_004_Import_Local_RPZ_Zone_With_Policy_Override_As_LOG_Only_And_Blank_Severity_Field_Verify_On_Import_Severity_Is_Changed_To_Major(self):
        
        display_msg("**********************************************")
        display_msg("*              Testcase 04                   *")
        display_msg("**********************************************")
        display_msg("Import local RPZ zone with policy override as LOG only and blank field for option Severity and after import verify that the severity is changed to Major")
        try:
            import_csv("test_004_local_rpz_zone_log_missing_severity.csv","OVERRIDE")
        except Exception as e:
            display_msg("The CSV import was successful, proceeding with further verification")
        
        restart_services()

        display_msg("Fetch rpz zone details and verify whether the severity has been changed to MAJOR")
        get_ref = ib_NIOS.wapi_request('GET',object_type="zone_rp?_return_fields=fqdn,rpz_severity") 
        display_msg(get_ref)
        for ref in json.loads(get_ref):
            if ref['fqdn'] == "log.com":
                if ref["rpz_severity"] == "MAJOR":
                    display_msg("CSV import is successful and the severity has been changed to MAJOR")
                    del_ref = ib_NIOS.wapi_request('DELETE',ref=ref['_ref'])
                    if bool(re.match("\"zone_rp*.",str(del_ref))):
                        sleep(10)
                        restart_services()
                        display_msg("RPZ zone deletion successful")
                        assert True
                    else:
                        restart_services()
                        display_msg("RPZ zone deletion failed but import was successful")
                        assert False

    @pytest.mark.run(order=5)
    def test_005_Import_Local_RPZ_Zone_With_Policy_Override_As_None_And_Missing_FQDN(self):
        
        display_msg("**********************************************")
        display_msg("*              Testcase 05                   *")
        display_msg("**********************************************")
        display_msg("Import local RPZ Zone with Policy override as None and the FQDN field containing blank value in the CSV file")
        import_csv("test_005_import_local_rpz_zone_None_policy_missing_name.csv","OVERRIDE")
        restart_services()

    @pytest.mark.run(order=6)
    def test_006_Import_Local_RPZ_Zone_With_Policy_Override_As_Block_No_Data_And_Missing_FQDN(self):
        
        display_msg("**********************************************")
        display_msg("*              Testcase 06                   *")
        display_msg("**********************************************")
        display_msg("Import local RPZ zone with Policy override as Block(No Data) and the FQDN field containing blank value in the CSV file")
        import_csv("test_006_import_rpz_substitute_zone_Block_No_Data_Missing_FQDN.csv","OVERRIDE")
        restart_services()

    @pytest.mark.run(order=7)
    def test_007_Import_Local_RPZ_Zone_With_Policy_Override_As_Block_No_Such_Domain_And_Missing_FQDN(self):
        
        display_msg("**********************************************")
        display_msg("*              Testcase 07                   *")
        display_msg("**********************************************")
        display_msg("Import local RPZ zone with Policy override as Block(No such domain) and the FQDN field containing blank value in the CSV file")
        import_csv("test_007_import_rpz_substitute_zone_Block_No_Such_Domain_Missing_FQDN.csv","OVERRIDE")
        restart_services()

    @pytest.mark.run(order=8)
    def test_008_Import_Local_RPZ_Zone_With_Policy_Override_As_Passthru_And_Missing_FQDN(self):
        
        display_msg("**********************************************")
        display_msg("*              Testcase 08                   *")
        display_msg("**********************************************")
        display_msg("Import local RPZ zone with Policy override as Passthru and the FQDN field containing blank value in the CSV file")
        import_csv("test_008_import_rpz_substitute_zone_Passthru_Missing_FQDN.csv","OVERRIDE")
        restart_services()

    @pytest.mark.run(order=9)
    def test_009_Import_Local_RPZ_Zone_With_Policy_Override_As_Substitute_Domain_Name_And_Missing_FQDN(self):
        
        display_msg("**********************************************")
        display_msg("*              Testcase 09                   *")
        display_msg("**********************************************")
        display_msg("Import local RPZ zone with Policy override as Substitute(Domain Name) and the FQDN field containing blank value in the CSV file")
        import_csv("test_009_import_rpz_substitute_zone_Substitute_Missing_FQDN.csv","OVERRIDE")
        restart_services()

    @pytest.mark.run(order=10)
    def test_010_Import_Local_RPZ_Zone_With_Policy_Override_As_Substitute_Domain_Name_And_Missing_Domain_Name(self):
        
        display_msg("**********************************************")
        display_msg("*              Testcase 10                   *")
        display_msg("**********************************************")
        display_msg("Import local RPZ zone with Policy override as Substitute(Domain Name) and the Domain name field containing blank value in the CSV file")
        import_csv("test_010_import_rpz_substitute_zone_Substitute_Missing_Domain_name.csv","OVERRIDE")
        restart_services()

    @pytest.mark.run(order=11)
    def test_011_Import_RPZ_Feed_With_Policy_Override_As_LOG_Only_And_Missing_Severity_Verify_If_Severity_Is_Changed_To_Major_On_Import(self):
        
        display_msg("**********************************************")
        display_msg("*              Testcase 11                   *")
        display_msg("**********************************************")
        display_msg("Import RPZ feed with policy override as LOG only and blank field for option Severity and after import verify that the severity is changed to Major")
        try:
            import_csv("test_011_import_rpz_feed_LOG_only_with_empty_severity_field.csv","OVERRIDE")
        except Exception as e:
            display_msg("The CSV import was successful, proceeding with further verification")
        
        restart_services()

        display_msg("Fetch rpz zone details and verify whether the severity has been changed to MAJOR")
        get_ref = ib_NIOS.wapi_request('GET',object_type="zone_rp?_return_fields=fqdn,rpz_severity") 
        display_msg(get_ref)
        for ref in json.loads(get_ref):
            if ref['fqdn'] == "testlog.com":
                if ref["rpz_severity"] == "MAJOR":
                    display_msg("CSV import is successful and the severity has been changed to MAJOR")
                    del_ref = ib_NIOS.wapi_request('DELETE',ref=ref['_ref'])
                    if bool(re.match("\"zone_rp*.",str(del_ref))):
                        sleep(10)
                        restart_services()
                        display_msg("RPZ zone deletion successful")
                        assert True
                    else:
                        restart_services()
                        display_msg("RPZ zone deletion failed but import was successful")
                        assert False



    @pytest.mark.run(order=12)
    def test_012_Import_RPZ_Feed_With_Policy_Override_As_None_And_Missing_FQDN(self):
        
        display_msg("**********************************************")
        display_msg("*              Testcase 12                   *")
        display_msg("**********************************************")
        display_msg("Import RPZ feed with Policy override as None and the FQDN field containing blank value in the CSV file")
        import_csv("test_012_import_rpz_feed_NONE_with_empty_FQDN.csv","OVERRIDE")
        restart_services()

    @pytest.mark.run(order=13)
    def test_013_Import_RPZ_Feed_With_Policy_Override_As_Block_No_Data_And_Missing_FQDN(self):
        
        display_msg("**********************************************")
        display_msg("*              Testcase 13                   *")
        display_msg("**********************************************")
        display_msg("Import RPZ feed with Policy override as Block(No Data) and the FQDN field containing blank value in the CSV file")
        import_csv("test_013_import_rpz_feed_Block_No_Data_with_empty_FQDN.csv","OVERRIDE")
        restart_services()

    @pytest.mark.run(order=14)
    def test_014_Import_RPZ_Feed_With_Policy_Override_As_Block_No_Such_Domain_And_Missing_FQDN(self):
        
        display_msg("**********************************************")
        display_msg("*              Testcase 14                   *")
        display_msg("**********************************************")
        display_msg("Import RPZ feed with Policy override as Block(No such domain) and the FQDN field containing blank value in the CSV file")
        import_csv("test_014_import_rpz_feed_Block_No_Such_Domain_with_empty_FQDN.csv","OVERRIDE")
        restart_services()

    @pytest.mark.run(order=15)
    def test_015_Import_RPZ_Feed_With_Policy_Override_As_Passthru_And_Missing_FQDN(self):
        
        display_msg("**********************************************")
        display_msg("*              Testcase 15                   *")
        display_msg("**********************************************")
        display_msg("Import RPZ feed with Policy override as Passthru and the FQDN field containing blank value in the CSV file")
        import_csv("test_015_import_rpz_feed_Passthru_with_empty_FQDN.csv","OVERRIDE")
        restart_services()

    @pytest.mark.run(order=16)
    def test_016_Import_RPZ_Feed_With_Policy_Override_As_Substitute_Domain_Name_And_Missing_FQDN(self):
        
        display_msg("**********************************************")
        display_msg("*              Testcase 16                   *")
        display_msg("**********************************************")
        display_msg("Import RPZ feed with Policy override as Substitute(Domain Name) and the FQDN field containing blank value in the CSV file")
        import_csv("test_016_import_rpz_feed_Substitute_Missing_FQDN.csv","OVERRIDE")
        restart_services()

    @pytest.mark.run(order=17)
    def test_017_Import_RPZ_Feed_With_Policy_Override_As_Substitute_Domain_Name_And_Missing_Domain_Name(self):
        
        display_msg("**********************************************")
        display_msg("*              Testcase 17                   *")
        display_msg("**********************************************")
        display_msg("Import RPZ feed with Policy override as Substitute(Domain Name) and the Domain name field containing blank value in the CSV file")
        import_csv("test_017_import_rpz_feed_Substitute_Missing_Domain_name.csv","OVERRIDE")
        restart_services()

    @pytest.mark.run(order=18)
    def test_018_Create_Local_RPZ_Domain(self):
        
        display_msg("**********************************************")
        display_msg("*              Testcase 18                   *")
        display_msg("**********************************************")
        display_msg("Creating Local RPZ domain zone.com")
        data = {"fqdn": "zone.com","grid_primary": [{"name": "infoblox.localdomain","stealth": False}],"rpz_policy": "NODATA","rpz_severity": "MAJOR"}
        response = ib_NIOS.wapi_request('POST',object_type='zone_rp',fields=json.dumps(data))
        display_msg(response)
        if bool(re.match("\"zone_rp*.",str(response))):
            display_msg("Local RPZ domain zone.com creation successful")
            assert True
        else:
            display_msg("Local RPZ domain zone.com creation failed")
            assert False

    @pytest.mark.run(order=19)
    def test_019_Import_RPZ_Passthru_Rule_Passthru_Domain_Rule_With_Missing_FQDN_Field(self):
        
        display_msg("**********************************************")
        display_msg("*              Testcase 19                   *")
        display_msg("**********************************************")
        display_msg("Import RPZ Passthru Rule(Pasthru Domain Rule) with missing FQDN field")
        import_csv("test_019_import_rpz_passthru_rule_passthru_domain_rule_with_missing_fqdn.csv","OVERRIDE")
        restart_services()


    @pytest.mark.run(order=20)
    def test_020_Import_RPZ_Passthru_Rule_Passthru_IP_Address_Rule_With_Missing_IP_Address_Or_Network(self):
        
        display_msg("**********************************************")
        display_msg("*              Testcase 20                   *")
        display_msg("**********************************************")
        display_msg("Import RPZ Passthru Rule(Passthru IP address Rule) with missing IP address/Network")
        import_csv("test_020_import_rpz_passthru_rule_passthru_ip_address_rule_with_missing_ip_address_or_network.csv","OVERRIDE")
        restart_services()


    @pytest.mark.run(order=21)
    def test_021_Import_RPZ_Passthru_Rule_Client_IP_Address_Rule_With_Missing_IP_Address_Or_Network(self):
        
        display_msg("**********************************************")
        display_msg("*              Testcase 21                   *")
        display_msg("**********************************************")
        display_msg("Import RPZ Passthru Rule(Client IP Address Rule) with missing IP address/Network")
        import_csv("test_021_import_rpz_passthru_rule_passthru_client_ip_address_rule_with_missing_ip_address_or_network.csv","OVERRIDE")
        restart_services()


    @pytest.mark.run(order=22)
    def test_022_Import_Block_No_Such_Domain_Rule_Block_No_Such_Domain_Rule_With_Missing_FQDN_Field(self):
        
        display_msg("**********************************************")
        display_msg("*              Testcase 22                   *")
        display_msg("**********************************************")
        display_msg("Import Block(No Such Domain) Rule(Block(No Such Domain)) with missing FQDN field")
        import_csv("test_022_import_block_no_such_domain_rule_block_no_such_domain_rule_with_missing_fqdn.csv","OVERRIDE")
        restart_services()


    @pytest.mark.run(order=23)
    def test_023_Import_Block_No_Such_Domain_Rule_Block_IP_Address_No_Such_Domain_Rule_With_Missing_IP_Address_Or_Network(self):
        
        display_msg("**********************************************")
        display_msg("*              Testcase 23                   *")
        display_msg("**********************************************")
        display_msg("Import Block(No Such Domain) Rule(Block IP Address(No Such Domain)) with missing IP Address/Network")
        import_csv("test_023_import_block_no_such_domain_rule_block_ip_address_no_such_domain_rule_with_missing_ip_or_network.csv","OVERRIDE")
        restart_services()


    @pytest.mark.run(order=24)
    def test_024_Import_Block_No_Such_Domain_Rule_Block_Client_IP_Address_No_Such_Domain_Rule_With_Missing_IP_Address_Or_Network(self):
        
        display_msg("**********************************************")
        display_msg("*              Testcase 24                   *")
        display_msg("**********************************************")
        display_msg("Import Block(No Such Domain) Rule(Block Client IP Address(No Such Domain)) with missing IP Address/Network")
        import_csv("test_024_import_block_no_such_domain_rule_block_client_ip_address_no_such_domain_rule_with_missing_ip_or_network.csv","OVERRIDE")
        restart_services()

    @pytest.mark.run(order=25)
    def test_025_Import_Block_No_Data_Rule_Block_Domain_Name_No_Data_Rule_With_Missing_FQDN(self):
        
        display_msg("**********************************************")
        display_msg("*              Testcase 25                   *")
        display_msg("**********************************************")
        display_msg("Import Block(No Data) Rule(Block Domain Name(No Data)) with missing FQDN")
        import_csv("test_025_import_block_no_data_rule_block_domain_name_no_data_missing_fqdn.csv","OVERRIDE")
        restart_services()


    @pytest.mark.run(order=26)
    def test_026_Import_Block_No_Data_Rule_Block_IP_Address_No_Data_Rule_With_Missing_IP_Address_Or_Network(self):
        
        display_msg("**********************************************")
        display_msg("*              Testcase 26                   *")
        display_msg("**********************************************")
        display_msg("Import Block(No Data) Rule(Block IP Address(No Data)) with missing ip address or network")
        import_csv("test_026_import_block_no_data_rule_block_ip_address_no_data_missing_ip_address_or_network.csv","OVERRIDE")
        restart_services()
    

    @pytest.mark.run(order=27)
    def test_027_Import_Block_No_Data_Rule_Block_Client_IP_Address_No_Data_Rule_With_Missing_IP_Address_Or_Network(self):
        
        display_msg("**********************************************")
        display_msg("*              Testcase 27                   *")
        display_msg("**********************************************")
        display_msg("Import Block(No Data) Rule(Block Client IP Address(No Data)) with missing FQDN")
        import_csv("test_027_import_block_no_data_rule_block_client_ip_address_no_data_missing_ip_address_or_network.csv","OVERRIDE")
        restart_services()


    @pytest.mark.run(order=28)
    def test_028_Import_RPZ_Substitute_Domain_Name_Domain_Name_Rule_With_Missing_FQDN(self):
        
        display_msg("**********************************************")
        display_msg("*              Testcase 28                   *")
        display_msg("**********************************************")
        display_msg("Import RPZ Substitute Domain(Domain Name) Rule with missing FQDN")
        import_csv("test_028_import_rpz_substitute_domain_name_domain_name_rule_with_missing_fqdn.csv","OVERRIDE")
        restart_services()


    @pytest.mark.run(order=29)
    def test_029_Import_RPZ_Substitute_Domain_Name_IP_Address_Rule_With_Missing_IP_Address_Field(self):
        
        display_msg("**********************************************")
        display_msg("*              Testcase 29                   *")
        display_msg("**********************************************")
        display_msg("Import RPZ Substitute Domain(IP Address) Rule with missing IP Address")
        import_csv("test_029_import_rpz_substitute_domain_name_ip_address_rule_with_missing_ip_address_or_network.csv","OVERRIDE")
        restart_services()


    @pytest.mark.run(order=30)
    def test_030_Import_RPZ_Substitute_Domain_Name_Client_IP_Address_Rule_With_Missing_IP_Address_Field(self):
        
        display_msg("**********************************************")
        display_msg("*              Testcase 30                   *")
        display_msg("**********************************************")
        display_msg("Import RPZ Substitute Domain(Client IP Address) Rule with missing IP Address")
        import_csv("test_030_import_rpz_substitute_domain_name_client_ip_address_rule_with_missing_ip_address_or_network.csv","OVERRIDE")
        restart_services()

    @pytest.mark.run(order=31)
    def test_031_Import_RPZ_A_Record_With_Missing_FQDN_Field(self):
        
        display_msg("**********************************************")
        display_msg("*              Testcase 31                   *")
        display_msg("**********************************************")
        display_msg("Import RPZ A record with missing FQDN field")
        import_csv("test_031_import_rpz_a_record_missing_fqdn.csv","OVERRIDE")
        restart_services()

    @pytest.mark.run(order=32)
    def test_032_Import_RPZ_A_Record_With_Missing_IPv4_Field(self):
        
        display_msg("**********************************************")
        display_msg("*              Testcase 32                   *")
        display_msg("**********************************************")
        display_msg("Import RPZ A record with missing IPv4 field")
        import_csv("test_032_import_rpz_a_record_missing_ip_address.csv","OVERRIDE")
        restart_services()


    @pytest.mark.run(order=33)
    def test_033_Import_RPZ_AAAA_Record_With_Missing_FQDN_Field(self):
        
        display_msg("**********************************************")
        display_msg("*              Testcase 33                   *")
        display_msg("**********************************************")
        display_msg("Import RPZ AAAA record with missing FQDN field")
        import_csv("test_033_import_rpz_aaaa_record_missing_fqdn.csv","OVERRIDE")
        restart_services()

    @pytest.mark.run(order=34)
    def test_034_Import_RPZ_AAAA_Record_With_Missing_IPv6_Field(self):
        
        display_msg("**********************************************")
        display_msg("*              Testcase 34                   *")
        display_msg("**********************************************")
        display_msg("Import RPZ AAAA record with missing IPv6 field")
        import_csv("test_034_import_rpz_aaaa_record_missing_ip_address.csv","OVERRIDE")
        restart_services()


    @pytest.mark.run(order=35)
    def test_035_Import_RPZ_TXT_Record_With_Missing_FQDN_Field(self):
        
        display_msg("**********************************************")
        display_msg("*              Testcase 35                   *")
        display_msg("**********************************************")
        display_msg("Import RPZ TXT record with missing FQDN field")
        import_csv("test_035_import_rpz_txt_record_with_missing_fqdn.csv","OVERRIDE")
        restart_services()

    @pytest.mark.run(order=36)
    def test_036_Import_RPZ_TXT_Record_With_Missing_Text_Field(self):
        
        display_msg("**********************************************")
        display_msg("*              Testcase 36                   *")
        display_msg("**********************************************")
        display_msg("Import RPZ TXT record with missing text field")
        import_csv("test_036_import_rpz_txt_record_with_missing_text.csv","OVERRIDE")
        restart_services()


    @pytest.mark.run(order=37)
    def test_037_Import_RPZ_NAPTR_Record_With_Missing_FQDN_Field(self):
        
        display_msg("**********************************************")
        display_msg("*              Testcase 37                   *")
        display_msg("**********************************************")
        display_msg("Import RPZ NAPTR record with missing FQDN field")
        import_csv("test_037_import_rpz_naptr_record_missing_fqdn.csv","OVERRIDE")
        restart_services()


    @pytest.mark.run(order=38)
    def test_038_Import_RPZ_PTR_Record_With_Missing_DNAME_Field(self):
        
        display_msg("**********************************************")
        display_msg("*              Testcase 38                   *")
        display_msg("**********************************************")
        display_msg("Import RPZ PTR record with missing dname field")
        import_csv("test_038_import_rpz_ptr_record_missing_dname.csv","OVERRIDE")
        restart_services()


    @pytest.mark.run(order=39)
    def test_039_Import_RPZ_SRV_Record_With_Missing_PORT_Field(self):
        
        display_msg("**********************************************")
        display_msg("*              Testcase 39                   *")
        display_msg("**********************************************")
        display_msg("Import RPZ SRV record with missing PORT field")
        import_csv("test_039_import_rpz_srv_record_missing_port.csv","OVERRIDE")
        restart_services()

    @pytest.mark.run(order=40)
    def test_040_Import_RPZ_SRV_Record_With_PORT_Number_Greater_Than_65535(self):
        
        display_msg("**********************************************")
        display_msg("*              Testcase 40                   *")
        display_msg("**********************************************")
        display_msg("Import RPZ SRV record with PORT number greater than 65535")
        import_csv("test_040_import_rpz_srv_record_port_number_greater_than_65535.csv","OVERRIDE")
        restart_services()

    @pytest.mark.run(order=41)
    def test_041_Import_RPZ_SRV_Record_With_Negative_Value_For_PORT_Number(self):
        
        display_msg("**********************************************")
        display_msg("*              Testcase 41                   *")
        display_msg("**********************************************")
        display_msg("Import RPZ SRV record with negative value for port number")
        import_csv("test_041_import_rpz_srv_record_port_number_negative_value.csv","OVERRIDE")
        restart_services()

    @pytest.mark.run(order=42)
    def test_042_Import_RPZ_IPv4_Address_Record_With_Empty_Address_Field(self):
        
        display_msg("**********************************************")
        display_msg("*              Testcase 42                   *")
        display_msg("**********************************************")
        display_msg("Import RPZ IPv4 address record with empty address field")
        import_csv("test_042_import_rpz_ipv4_address_record_missing_address_field.csv","OVERRIDE")
        restart_services()

    @pytest.mark.run(order=43)
    def test_043_Import_RPZ_IPv6_Address_Record_With_Empty_Address_Field(self):
        
        display_msg("**********************************************")
        display_msg("*              Testcase 43                   *")
        display_msg("**********************************************")
        display_msg("Import RPZ IPv6 address record with empty address field")
        import_csv("test_043_import_rpz_ipv6_address_record_missing_address_field.csv","OVERRIDE")
        restart_services()

    @pytest.mark.run(order=44)
    def test_044_Test_Cleanup(self):
        
        display_msg("**********************************************")
        display_msg("*              Testcase 44                   *")
        display_msg("**********************************************")
        display_msg("Starting test cleanup")
        get_ref = ib_NIOS.wapi_request('GET',object_type="zone_rp?_return_fields=fqdn")
        display_msg("Logging all rpz zone details")
        display_msg(get_ref)

        for ref in json.loads(get_ref):
            if ref['fqdn'] == 'zone.com':
                response = ib_NIOS.wapi_request('DELETE',ref = ref['_ref'])
                display_msg(response)
                if bool(re.match("\"zone_rp*.",str(response))):
                    display_msg("RPZ zone test.com deleted successfully")
                    restart_services()
                    assert True
                else:
                     display_msg("RPZ zone test.com deletion unsuccessfull")
                     assert False

        display_msg("Fetching grid master reference")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member")
        master_ref=''
        for ref in json.loads(get_ref):
            if ref['host_name'] == "infoblox.localdomain":
                master_ref = ref['_ref']
                display_msg(master_ref)
                break
        if master_ref == '':
            display_msg("Reference of master grid not found")
            assert False
        display_msg("Changing the hostname of master grid to "+config.grid_fqdn)
        data = {"host_name": config.grid_fqdn}
        response = ib_NIOS.wapi_request('PUT', ref=master_ref, fields=json.dumps(data))
        if bool(re.match("\"member*.",str(response))):
            display_msg("Hostname of master changed successfully")
            sleep(180)
            assert True
        else:
            display_msg("Changing hostname of the master failed")
            assert False



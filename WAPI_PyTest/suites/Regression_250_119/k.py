import config
import os
import ib_utils.ib_papi as papi
import ib_data.ib_preparation as prep
from time import sleep
os.environ["PYTHONPATH"]=os.getcwd()
#papi.add_rpz_data()
#papi.add_analityics_data(config.grid_member5_vip)
#papi.add_threate_protection_data(config.grid_member5_vip)
#prep.threat_protection_reports()
#prep.security_rpz_reports()
#papi.enable_mgmt(config.grid_vip,config.grid_member5_vip)
#papi.enable_forwarder_and_recusion(config.grid_vip)
#papi.add_analityics_data(config.grid_member5_vip)
#prep.dns_top_requested_domain_names()
#prep.dns_top_clients()
#sleep(60)
print "---"
print config.grid2_vip
print "---"
print config.grid2_fqdn
prep.rpz_security()
#prep.dhcp_fingerprint()
#prep.dhcp_top_lease_clients()
#sleep(60)
#prep.dns_top_timed_out_recursive_queries()
#sleep(60)
#prep.dns_top_nxdomain_noerror()
#sleep(60)
#prep.dns_top_clients_per_domain()

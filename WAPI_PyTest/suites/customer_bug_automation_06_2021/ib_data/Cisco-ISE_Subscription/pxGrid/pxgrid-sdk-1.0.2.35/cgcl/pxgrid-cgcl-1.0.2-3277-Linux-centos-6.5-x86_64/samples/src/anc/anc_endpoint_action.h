#include "pxgrid.h"

void anc_apply_endpoint_policy_by_mac_request(pxgrid_connection *connection, pxgrid_capability *capability, char *policy_name, char *mac);
void anc_apply_endpoint_policy_by_ip_request(pxgrid_connection *connection, pxgrid_capability *capability, char *policy_name, char *ip);
void anc_clear_endpoint_policy_by_mac_request(pxgrid_connection *connection, pxgrid_capability *capability, char *mac);	
void anc_clear_endpoint_policy_by_ip_request(pxgrid_connection *connection, pxgrid_capability *capability, char *ip);

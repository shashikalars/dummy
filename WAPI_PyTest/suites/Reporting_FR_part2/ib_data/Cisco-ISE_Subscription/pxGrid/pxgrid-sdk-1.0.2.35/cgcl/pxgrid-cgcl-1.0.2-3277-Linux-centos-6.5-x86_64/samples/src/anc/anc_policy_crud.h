#include "pxgrid.h"
#include "helper.h"

PXGRID_STATUS anc_createPolicyRequest(pxgrid_connection *connection, pxgrid_capability *capability, char *name, int *actions);
PXGRID_STATUS anc_updatePolicyRequest(pxgrid_connection *connection, pxgrid_capability *capability, char *name, int *actions);
PXGRID_STATUS anc_deletePolicyRequest(pxgrid_connection *connection, pxgrid_capability *capability, char * name);
PXGRID_STATUS anc_getPolicyByName(pxgrid_connection *connection, pxgrid_capability *capability, char *name);
PXGRID_STATUS anc_getAllPolicies(pxgrid_connection *connection, pxgrid_capability *capability);

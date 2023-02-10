#include "pxgrid.h"

PXGRID_STATUS anc_getEndpointByMACRequest(pxgrid_connection *connection, pxgrid_capability *capability, char *mac);
PXGRID_STATUS anc_getEndpointByIPRequest(pxgrid_connection *connection, pxgrid_capability *capability, char *ip);
PXGRID_STATUS anc_getAllEndpointsRequest(pxgrid_connection *connection, pxgrid_capability *capability);
PXGRID_STATUS anc_getEndpointByPolicyRequest(pxgrid_connection *connection, pxgrid_capability *capability, char *name);

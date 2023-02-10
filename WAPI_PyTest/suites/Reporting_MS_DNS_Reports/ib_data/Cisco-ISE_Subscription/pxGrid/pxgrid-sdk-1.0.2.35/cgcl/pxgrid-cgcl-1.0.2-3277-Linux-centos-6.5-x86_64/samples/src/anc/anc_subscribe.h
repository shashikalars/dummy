#include "pxgrid.h"
#define UNUSED(x) (void)(x)

void subscribe(pxgrid_connection *connection);
void message_callback(jw_dom_node *node, void *arg);
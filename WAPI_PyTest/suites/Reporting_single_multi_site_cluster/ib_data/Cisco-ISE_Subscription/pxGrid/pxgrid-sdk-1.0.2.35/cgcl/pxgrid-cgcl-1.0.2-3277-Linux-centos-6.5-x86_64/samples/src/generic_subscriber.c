#include <stdlib.h>
#include <unistd.h>
#include <memory.h>
#include "pxgrid.h"
#include "helper.h"

#include <openssl/ssl.h>
#define UNUSED(x) (void)(x)

static void subscribe_callback(jw_dom_node *node, void *arg) {
    UNUSED(arg);
    printf("Received notification\n");
    helper_print_jw_dom(node);
}

int main(int argc, char **argv) {
    helper_connection *hconn;
    helper_connection_create(&hconn, argc, argv);
    helper_connection_connect(hconn);
    
    char cap_name[128];
    helper_prompt("Enter capability name for subscription: ", cap_name);
    
    pxgrid_connection *connection = hconn->connection;
    
    const char pxgrid_ns[] = "http://www.cisco.com/pxgrid";
    
    pxgrid_capability *capability;
    pxgrid_capability_create(&capability);
    pxgrid_dynamic_capability_set_name(capability, cap_name);
    pxgrid_capability_set_namespace(capability, pxgrid_ns);

    pxgrid_dynamic_capability_subscribe(capability, connection);
    pxgrid_connection_register_notification_handler(connection, pxgrid_ns, "genericMessage", subscribe_callback, NULL);
    
    helper_prompt("press <enter> to disconnect...\n", NULL);

    helper_connection_disconnect(hconn);
    helper_connection_destroy(hconn);

    return 0;
}


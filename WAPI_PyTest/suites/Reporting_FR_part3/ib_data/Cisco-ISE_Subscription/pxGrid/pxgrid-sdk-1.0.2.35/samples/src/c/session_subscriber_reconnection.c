#include "pxgrid.h"
#include "helper.h"

#define UNUSED(x) (void)(x)

static void subscribe_callback(jw_dom_node *node, void *arg) {
    UNUSED(arg);
    printf("Received notification\n");
	helper_print_jw_dom(node);
}

int main(int argc, char **argv) {
    pxgrid_connection *connection;
    pxgrid_reconnection *reconnection;
    helper_connection *hconn;
    
    helper_connection_create(&hconn, argc, argv);
    connection = helper_connection_get_pxgrid_connection(hconn);
    pxgrid_reconnection_create(&reconnection, connection);
    pxgrid_reconnection_start(reconnection);

	char namespace[] = "http://www.cisco.com/pxgrid/identity";
    char name[] = "SessionDirectoryCapability";
    char sess_notif[] = "sessionNotification";
    
	pxgrid_capability *capability = NULL;
	pxgrid_capability_create(&capability);
	pxgrid_capability_set_namespace(capability, namespace);
	pxgrid_capability_set_name(capability, name);
	pxgrid_capability_subscribe(capability, connection);
      
    pxgrid_connection_register_notification_handler(connection, namespace, sess_notif, subscribe_callback, NULL);

    helper_prompt("press <enter> to disconnect...\n", NULL);
    pxgrid_reconnection_stop(reconnection);
    pxgrid_reconnection_destroy(reconnection);
    helper_connection_destroy(hconn);

  	return 0;
}


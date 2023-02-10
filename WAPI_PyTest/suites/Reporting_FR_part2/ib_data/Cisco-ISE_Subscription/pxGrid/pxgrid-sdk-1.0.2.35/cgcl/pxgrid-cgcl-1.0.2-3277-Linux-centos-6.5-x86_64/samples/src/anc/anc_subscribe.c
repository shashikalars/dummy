#include "anc_subscribe.h"
#include "helper.h"

void subscribe(pxgrid_connection *connection) {
	const char ns_iden[] = "http://www.cisco.com/pxgrid/anc";
	const char apply_endpoint_policy_notif[] = "ApplyEndpointPolicyNotification";
	pxgrid_connection_register_notification_handler(connection, ns_iden, apply_endpoint_policy_notif, message_callback, NULL);
	const char clear_endpoint_policy_notif[] = "ClearEndpointPolicyNotification";
	pxgrid_connection_register_notification_handler(connection, ns_iden, clear_endpoint_policy_notif, message_callback, NULL);
	const char create_policy_notif[] = "CreatePolicyNotification";
	pxgrid_connection_register_notification_handler(connection, ns_iden, create_policy_notif, message_callback, NULL);
	const char delete_policy_notif[] = "DeletePolicyNotification";
	pxgrid_connection_register_notification_handler(connection, ns_iden, delete_policy_notif, message_callback, NULL);
	const char update_policy_notif[] = "UpdatePolicyNotification";
	pxgrid_connection_register_notification_handler(connection, ns_iden, update_policy_notif, message_callback, NULL);

}

void message_callback(jw_dom_node *node, void *arg) {
	UNUSED(arg);
	helper_print_jw_dom(node);
}
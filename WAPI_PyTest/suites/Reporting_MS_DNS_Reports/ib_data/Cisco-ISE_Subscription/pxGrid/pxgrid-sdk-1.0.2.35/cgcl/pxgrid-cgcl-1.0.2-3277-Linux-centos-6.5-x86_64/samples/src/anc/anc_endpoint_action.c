#include "anc_endpoint_action.h"
#include "helper.h"


void anc_apply_endpoint_policy_by_mac_request(pxgrid_connection *connection, pxgrid_capability *capability, char *policy_name, char *mac_address) {
	jw_err err;
    jw_dom_ctx_type *ctx;
    jw_dom_node *anc_policy_name;
    jw_dom_node *anc_policy_name_text;
    jw_dom_node *anc_mac_address;
    jw_dom_node *anc_mac_address_text;
    jw_dom_node *request;
    jw_dom_node *response;

    if (!jw_dom_context_create(&ctx, &err)
        || !jw_dom_element_create(ctx, "{http://www.cisco.com/pxgrid/anc}applyEndpointPolicyByMACRequest", &request, &err)
        || !jw_dom_element_create(ctx, "{http://www.cisco.com/pxgrid/anc}policyName", &anc_policy_name, &err)
        || !jw_dom_add_child(request, anc_policy_name, &err)
        || !jw_dom_text_create(ctx, policy_name, &anc_policy_name_text, &err)
        || !jw_dom_add_child(anc_policy_name, anc_policy_name_text, &err)
        || !jw_dom_element_create(ctx, "{http://www.cisco.com/pxgrid/anc}macAddress", &anc_mac_address, &err)
        || !jw_dom_add_child(request, anc_mac_address, &err)
        || !jw_dom_text_create(ctx, mac_address, &anc_mac_address_text, &err)
        || !jw_dom_add_child(anc_mac_address, anc_mac_address_text, &err)
        )
    {
        jw_log_err(JW_LOG_ERROR, &err, "query");
        return;
    }

    printf("***request\n");
    helper_print_jw_dom(request);

    PXGRID_STATUS status = pxgrid_connection_query(connection, capability, request, &response);
	if (status == PXGRID_STATUS_OK) {
		printf("*** response\n");
		helper_print_jw_dom(response);	
		printf("*** queried\n");
	}	
	else {
		printf("status=%s\n", pxgrid_status_get_message(status));
	}	
}

void anc_apply_endpoint_policy_by_ip_request(pxgrid_connection *connection, pxgrid_capability *capability, char *policy_name, char *ip) {
	jw_err err;
    jw_dom_ctx_type *ctx;
    jw_dom_node *anc_policy_name;
    jw_dom_node *anc_policy_name_text;
    jw_dom_node *anc_ip_identifier;
    jw_dom_node *anc_ip_address;
    jw_dom_node *anc_ip_address_text;
    jw_dom_node *request;
    jw_dom_node *response;

    if (!jw_dom_context_create(&ctx, &err)
        || !jw_dom_element_create(ctx, "{http://www.cisco.com/pxgrid/anc}applyEndpointPolicyByIPRequest", &request, &err)
        || !jw_dom_element_create(ctx, "{http://www.cisco.com/pxgrid/anc}policyName", &anc_policy_name, &err)
        || !jw_dom_add_child(request, anc_policy_name, &err)
        || !jw_dom_text_create(ctx, policy_name, &anc_policy_name_text, &err)
        || !jw_dom_add_child(anc_policy_name, anc_policy_name_text, &err)
        || !jw_dom_element_create(ctx, "{http://www.cisco.com/pxgrid/anc}ipIdentifier", &anc_ip_identifier, &err)
        || !jw_dom_add_child(request, anc_ip_identifier, &err)
        || !jw_dom_element_create(ctx, "{http://www.cisco.com/pxgrid/anc}ipAddress", &anc_ip_address, &err)
        || !jw_dom_add_child(anc_ip_identifier, anc_ip_address, &err)
		|| !jw_dom_text_create(ctx, ip, &anc_ip_address_text, &err) 
		|| !jw_dom_add_child(anc_ip_address, anc_ip_address_text, &err)
        )
    {
        jw_log_err(JW_LOG_ERROR, &err, "query");
        return;
    }

    printf("***request\n");
    helper_print_jw_dom(request);

    PXGRID_STATUS status = pxgrid_connection_query(connection, capability, request, &response);
	if (status == PXGRID_STATUS_OK) {
		printf("*** response\n");
		helper_print_jw_dom(response);	
		printf("*** queried\n");
	}	
	else {
		printf("status=%s\n", pxgrid_status_get_message(status));
	}	
}

void anc_clear_endpoint_policy_by_mac_request(pxgrid_connection *connection, pxgrid_capability *capability, char *mac_address) {
	jw_err err;
    jw_dom_ctx_type *ctx;
    jw_dom_node *anc_mac_address;
    jw_dom_node *anc_mac_address_text;
    jw_dom_node *request;
    jw_dom_node *response;

    if (!jw_dom_context_create(&ctx, &err)
        || !jw_dom_element_create(ctx, "{http://www.cisco.com/pxgrid/anc}clearEndpointPolicyByMACRequest", &request, &err)
        || !jw_dom_element_create(ctx, "{http://www.cisco.com/pxgrid/anc}macAddress", &anc_mac_address, &err)
        || !jw_dom_add_child(request, anc_mac_address, &err)
        || !jw_dom_text_create(ctx, mac_address, &anc_mac_address_text, &err)
        || !jw_dom_add_child(anc_mac_address, anc_mac_address_text, &err)
        )
    {
        jw_log_err(JW_LOG_ERROR, &err, "query");
        return;
    }

    printf("***request\n");
    helper_print_jw_dom(request);

    PXGRID_STATUS status = pxgrid_connection_query(connection, capability, request, &response);
	if (status == PXGRID_STATUS_OK) {
		printf("*** response\n");
		helper_print_jw_dom(response);	
		printf("*** queried\n");
	}	
	else {
		printf("status=%s\n", pxgrid_status_get_message(status));
	}	
}

void anc_clear_endpoint_policy_by_ip_request(pxgrid_connection *connection, pxgrid_capability *capability, char *ip) {
	jw_err err;
    jw_dom_ctx_type *ctx;
    jw_dom_node *anc_ip_identifier;
    jw_dom_node *anc_ip_address;
    jw_dom_node *anc_ip_address_text;
    jw_dom_node *request;
    jw_dom_node *response;

    if (!jw_dom_context_create(&ctx, &err)
        || !jw_dom_element_create(ctx, "{http://www.cisco.com/pxgrid/anc}clearEndpointPolicyByIPRequest", &request, &err)
        || !jw_dom_element_create(ctx, "{http://www.cisco.com/pxgrid/anc}ipIdentifier", &anc_ip_identifier, &err)
        || !jw_dom_add_child(request, anc_ip_identifier, &err)
        || !jw_dom_element_create(ctx, "{http://www.cisco.com/pxgrid/anc}ipAddress", &anc_ip_address, &err)
        || !jw_dom_add_child(anc_ip_identifier, anc_ip_address, &err)
		|| !jw_dom_text_create(ctx, ip, &anc_ip_address_text, &err) 
		|| !jw_dom_add_child(anc_ip_address, anc_ip_address_text, &err)
        )
    {
        jw_log_err(JW_LOG_ERROR, &err, "query");
        return;
    }

    printf("***request\n");
    helper_print_jw_dom(request);

    PXGRID_STATUS status = pxgrid_connection_query(connection, capability, request, &response);
	if (status == PXGRID_STATUS_OK) {
		printf("*** response\n");
		helper_print_jw_dom(response);	
		printf("*** queried\n");
	}	
	else {
		printf("status=%s\n", pxgrid_status_get_message(status));
	}
}




#include "helper.h"
#include "anc_endpoint_read.h"

PXGRID_STATUS anc_getEndpointByMACRequest(pxgrid_connection *connection, pxgrid_capability *capability, char *mac) {
    PXGRID_STATUS status = PXGRID_STATUS_OK;
    
    jw_err err;
    jw_dom_ctx_type *ctx;
    jw_dom_node *mac_address;
    jw_dom_node *mac_address_text;
    jw_dom_node *request;
    jw_dom_node *response;

    /*
    <getEndpointByMACRequest xmlns='http://www.cisco.com/pxgrid/anc'>
        <macAddress>00:0C:29:2E:41:4A</macAddress>
    </getEndpointByMACRequest>
    */

    if (!jw_dom_context_create(&ctx, &err)
        || !jw_dom_element_create(ctx, "{http://www.cisco.com/pxgrid/anc}getEndpointByMACRequest", &request, &err)
        || !jw_dom_element_create(ctx, "{http://www.cisco.com/pxgrid/anc}macAddress", &mac_address, &err)
        || !jw_dom_add_child(request, mac_address, &err)
        || !jw_dom_text_create(ctx, mac, &mac_address_text, &err)
        || !jw_dom_add_child(mac_address, mac_address_text, &err)
        )
    {
        jw_log_err(JW_LOG_ERROR, &err, "query");
        return PXGRID_STATUS_JW_ERROR;
    }

    printf("***request\n");
    helper_print_jw_dom(request);

    status = pxgrid_connection_query(connection, capability, request, &response);
    printf("status=%s\n", pxgrid_status_get_message(status));

    printf("***response\n");
    helper_print_jw_dom(response);

    if(ctx) jw_dom_context_destroy(ctx);

    return status;
}

PXGRID_STATUS anc_getEndpointByIPRequest(pxgrid_connection *connection, pxgrid_capability *capability, char *ip) {
    PXGRID_STATUS status = PXGRID_STATUS_OK;
    
    jw_err err;
    jw_dom_ctx_type *ctx;
    jw_dom_node *ip_identifier;
    jw_dom_node *ip_address;
    jw_dom_node *ip_address_text;
    jw_dom_node *request;
    jw_dom_node *response;

    /*
    <getEndpointByIPRequest xmlns='http://www.cisco.com/pxgrid/anc'>
        <ipIdentifier>
            <ipAddress xmlns='http://www.cisco.com/pxgrid'>10.23.23.2</ipAddress>
        </ipIdentifier>
    </getEndpointByIPRequest>
    */

    if (!jw_dom_context_create(&ctx, &err)
        || !jw_dom_element_create(ctx, "{http://www.cisco.com/pxgrid/anc}getEndpointByIPRequest", &request, &err)
        || !jw_dom_element_create(ctx, "{http://www.cisco.com/pxgrid/anc}ipIdentifier", &ip_identifier, &err)
        || !jw_dom_add_child(request, ip_identifier, &err)
        || !jw_dom_element_create(ctx, "{http://www.cisco.com/pxgrid}ipAddress", &ip_address, &err)
        || !jw_dom_add_child(ip_identifier, ip_address, &err)
        || !jw_dom_text_create(ctx, ip, &ip_address_text, &err)
        || !jw_dom_add_child(ip_address, ip_address_text, &err)
        )
    {
        jw_log_err(JW_LOG_ERROR, &err, "query");
        return PXGRID_STATUS_JW_ERROR;
    }

    printf("***request\n");
    helper_print_jw_dom(request);

    status = pxgrid_connection_query(connection, capability, request, &response);
    printf("status=%s\n", pxgrid_status_get_message(status));

    printf("***response\n");
    helper_print_jw_dom(response);

    if(ctx) jw_dom_context_destroy(ctx);

    return status;
}

PXGRID_STATUS anc_getAllEndpointsRequest(pxgrid_connection *connection, pxgrid_capability *capability) {
    PXGRID_STATUS status = PXGRID_STATUS_OK;
    
    jw_err err;
    jw_dom_ctx_type *ctx;
    jw_dom_node *request;
    jw_dom_node *response;

    /*
    <getAllEndpointsRequest xmlns='http://www.cisco.com/pxgrid/anc'/>
    */

    if (!jw_dom_context_create(&ctx, &err)
        || !jw_dom_element_create(ctx, "{http://www.cisco.com/pxgrid/anc}getAllEndpointsRequest", &request, &err)
        )
    {
        jw_log_err(JW_LOG_ERROR, &err, "query");
        return PXGRID_STATUS_JW_ERROR;
    }

    printf("***request\n");
    helper_print_jw_dom(request);

    status = pxgrid_connection_query(connection, capability, request, &response);
    printf("status=%s\n", pxgrid_status_get_message(status));

    printf("***response\n");
    helper_print_jw_dom(response);

    if(ctx) jw_dom_context_destroy(ctx);

    return status;
}

PXGRID_STATUS anc_getEndpointByPolicyRequest(pxgrid_connection *connection, pxgrid_capability *capability, char *name) {
    PXGRID_STATUS status = PXGRID_STATUS_OK;

    jw_err err;
    jw_dom_ctx_type *ctx;
    jw_dom_node *anc_policy_name;
    jw_dom_node *anc_policy_name_text;
    jw_dom_node *request;
    jw_dom_node *response;

    /*
    <getEndpointByPolicyRequest xmlns='http://www.cisco.com/pxgrid/anc'>
        <name>xGridANCpolicy</name>
    </getEndpointByPolicyRequest>
    */

    if (!jw_dom_context_create(&ctx, &err)
        || !jw_dom_element_create(ctx, "{http://www.cisco.com/pxgrid/anc}getEndpointByPolicyRequest", &request, &err)
        || !jw_dom_element_create(ctx, "{http://www.cisco.com/pxgrid/anc}name", &anc_policy_name, &err)
        || !jw_dom_add_child(request, anc_policy_name, &err)
        || !jw_dom_text_create(ctx, name, &anc_policy_name_text, &err)
        || !jw_dom_add_child(anc_policy_name, anc_policy_name_text, &err)
        )
    {
        jw_log_err(JW_LOG_ERROR, &err, "query");
        return PXGRID_STATUS_JW_ERROR;
    }

    printf("***request\n");
    helper_print_jw_dom(request);

    status = pxgrid_connection_query(connection, capability, request, &response);
    printf("status=%s\n", pxgrid_status_get_message(status));

    printf("***response\n");
    helper_print_jw_dom(response);

    if(ctx) jw_dom_context_destroy(ctx);

    return status;
}

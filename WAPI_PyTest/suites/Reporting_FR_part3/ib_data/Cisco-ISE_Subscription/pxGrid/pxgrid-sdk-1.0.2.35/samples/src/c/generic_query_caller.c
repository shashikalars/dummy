#include <stdlib.h>
#include <unistd.h>
#include <memory.h>
#include "pxgrid.h"
#include "helper.h"

#include <openssl/ssl.h>

static PXGRID_STATUS query_call(pxgrid_connection *connection, pxgrid_capability *capability, const char* capability_name, const char* operation_name, char *query_action_data) {
    jw_err err;
    jw_dom_ctx_type *ctx = NULL;
    jw_dom_node *request = NULL;
    jw_dom_node *body = NULL;
    
    if (!jw_dom_context_create(&ctx, &err)
        || !jw_dom_element_create(ctx, "{http://www.cisco.com/pxgrid}genericMessage", &request, &err)
        || !jw_dom_put_namespace(request, "", "http://www.cisco.com/pxgrid", &err)
        || !helper_jw_dom_add_child_with_text(request, "{http://www.cisco.com/pxgrid}capabilityName", capability_name, &err)
        || !helper_jw_dom_add_child_with_text(request, "{http://www.cisco.com/pxgrid}operationName", operation_name, &err)
        || !helper_jw_dom_add_child_with_text(request, "{http://www.cisco.com/pxgrid}messageType", "request", &err)
        || !jw_dom_element_create(ctx, "{http://www.cisco.com/pxgrid}body", &body, &err)
        || !jw_dom_add_child(request, body, &err)
        || !helper_jw_dom_add_child_with_text(body, "{http://www.cisco.com/pxgrid}content", query_action_data, &err)
        )
    {
        jw_log_err(JW_LOG_ERROR, &err, "xgrid generic client request create dom");
        return PXGRID_STATUS_PXGRID_ERROR;
    }

    printf("Sent request\n");
    helper_print_jw_dom(request);

    jw_dom_node *response = NULL;
    PXGRID_STATUS status = pxgrid_connection_query(connection, capability, request, &response);
    
    if (status == PXGRID_STATUS_OK) {
        printf("Received response\n");
        helper_print_jw_dom(response);
    }
    else {
        helper_print_error(status);
    }
    return status;
}

int main(int argc, char **argv) {
    helper_connection *hconn;
    helper_connection_create(&hconn, argc, argv);
    helper_connection_connect(hconn);
    
    char cap_name[128];
    helper_prompt("Enter capability name for query operation: ", cap_name);

    pxgrid_connection *connection = hconn->connection;

    pxgrid_capability *capability;
    pxgrid_capability_create(&capability);
    pxgrid_capability_set_namespace(capability, "http://www.cisco.com/pxgrid");
    pxgrid_dynamic_capability_set_name(capability, cap_name);

    pxgrid_dynamic_capability_subscribe(capability, connection);
    
    char operation_name[128];
    char capability_query_data[4096];
    while ((helper_prompt("\nQuery operation (or <enter> to quit): ", operation_name))
            && (helper_prompt("Query data (or <enter> to quit): ", capability_query_data))) {
        query_call(connection, capability, cap_name, operation_name, capability_query_data);
    }

    helper_connection_disconnect(hconn);
    helper_connection_destroy(hconn);
    
    return 0;
}


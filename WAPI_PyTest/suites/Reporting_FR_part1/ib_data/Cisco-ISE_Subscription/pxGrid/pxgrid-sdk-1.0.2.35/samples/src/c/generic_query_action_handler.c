#include <stdlib.h>
#include <unistd.h>
#include <memory.h>
#include <openssl/ssl.h>

#include "pxgrid.h"
#include "helper.h"

#define UNUSED(x) (void)(x)

static jw_dom_node *create_response(const char *capability_name, const char *operation_name, const char *data) {
    jw_err err;
    jw_dom_ctx_type *ctx = NULL;
    jw_dom_node* response = NULL;
    jw_dom_node *body = NULL;
    
    if (!jw_dom_context_create(&ctx, &err)
        || !jw_dom_element_create(ctx, "{http://www.cisco.com/pxgrid}genericMessage", &response, &err)
        || !jw_dom_put_namespace(response, "", "http://www.cisco.com/pxgrid", &err)
        || !helper_jw_dom_add_child_with_text(response, "{http://www.cisco.com/pxgrid}capabilityName", capability_name, &err)
        || !helper_jw_dom_add_child_with_text(response, "{http://www.cisco.com/pxgrid}operationName", operation_name, &err)
        || !helper_jw_dom_add_child_with_text(response, "{http://www.cisco.com/pxgrid}messageType", "response", &err)
        || !jw_dom_element_create(ctx, "{http://www.cisco.com/pxgrid}body", &body, &err)
        || !jw_dom_add_child(response, body, &err)
        || !helper_jw_dom_add_child_with_text(body, "{http://www.cisco.com/pxgrid}content", data, &err)
       )
    {
       jw_log_err(JW_LOG_ERROR, &err, "create_response failure");
       return NULL;
    }
    
    return response;
}

static jw_dom_node *create_unauthorized_response() {
    jw_err err;
    jw_dom_ctx_type *ctx = NULL;
    jw_dom_node *response = NULL;
    jw_dom_node *error_node = NULL;
    
    if (!jw_dom_context_create(&ctx, &err)
        || !jw_dom_element_create(ctx, "{http://www.cisco.com/pxgrid}genericMessage", &response, &err)
        || !jw_dom_put_namespace(response, "", "http://www.cisco.com/pxgrid", &err)
        || !jw_dom_element_create(ctx, "{http://www.cisco.com/pxgrid}error", &error_node, &err)
        || !helper_jw_dom_add_child_with_text(error_node, "{http://www.cisco.com/pxgrid}description", "not authorized", &err)
        || !jw_dom_add_child(response, error_node, &err)
        || !helper_jw_dom_add_child_with_text(response, "{http://www.cisco.com/pxgrid}messageType", "response", &err)
        )
    {
        jw_log_err(JW_LOG_ERROR, &err, "create_error failure");
        return NULL;
    }
    return response;
}

static jw_dom_node* query_handler_cb(jw_dom_node *request, void *arg) {
    pxgrid_connection *connection = (pxgrid_connection *)arg;
    if (!connection) return NULL;

    printf("Received request\n");
    helper_print_jw_dom(request);

    // To be filled in by user - Sample Data
    char *response_data = "SampleData";

    char user[128];
    if (pxgrid_xml_get_sender(request, user) != PXGRID_STATUS_OK) return NULL;

    jw_dom_node *genericmsg = request;

    jw_dom_node *capability_node = jw_dom_get_first_element(genericmsg, "capabilityName");
    if (!capability_node) {
        jw_log(JW_LOG_ERROR, "get capability_node failed");
        return NULL;
    }
    const char *capability_name = jw_dom_get_first_text(capability_node);

    jw_dom_node *operation_node = jw_dom_get_first_element(genericmsg, "operationName");
    if (!operation_node) {
        jw_log(JW_LOG_ERROR, "get operation_node failed");
        return NULL;
    }
    const char *operation_name = jw_dom_get_first_text(operation_node);

    jw_dom_node* response = NULL; 

    bool is_authz = pxgrid_connection_is_authorized(connection, capability_name, operation_name, user);
    if (is_authz) {
        response = create_response(capability_name, operation_name, response_data);
    }
    else {
        response = create_unauthorized_response();
    }

    printf("Sent response\n");
    helper_print_jw_dom(response);
    return response;
}

int main(int argc, char **argv) {
    helper_connection *hconn;
    helper_connection_create(&hconn, argc, argv);
    helper_connection_connect(hconn);
    
    char cap_name[128];
    helper_prompt("Enter capability name for query handling: ", cap_name);
    
    pxgrid_connection *connection = hconn->connection;
    
    pxgrid_capability *capability;
    pxgrid_capability_create(&capability);
    pxgrid_capability_set_namespace(capability, "http://www.cisco.com/pxgrid");
    pxgrid_dynamic_capability_set_name(capability, cap_name);
    pxgrid_dynamic_capability_publish(capability, connection);
    
    pxgrid_connection_register_query_handler(connection, "http://www.cisco.com/pxgrid", "genericMessage", query_handler_cb, connection);

    helper_prompt("press <enter> to disconnect...\n", NULL);
    
    helper_connection_disconnect(hconn);
    helper_connection_destroy(hconn);
    return 0;
}


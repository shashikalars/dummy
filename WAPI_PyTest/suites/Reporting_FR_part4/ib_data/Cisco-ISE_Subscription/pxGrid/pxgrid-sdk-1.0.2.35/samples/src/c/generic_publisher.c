#include <stdlib.h>
#include <unistd.h>
#include <memory.h>
#include "pxgrid.h"
#include "helper.h"

#include <openssl/ssl.h>
#define UNUSED(x) (void)(x)

PXGRID_STATUS _dynamic_capability_publish_data(pxgrid_connection *connection, pxgrid_capability *capability, const char* capability_name, const char* operation_name, char *publish_data) {jw_err err;
    jw_dom_ctx_type *ctx = NULL;
    jw_dom_node *notf = NULL;
    jw_dom_node *body = NULL;
    
    if (!jw_dom_context_create(&ctx, &err)
        || !jw_dom_element_create(ctx, "{http://www.cisco.com/pxgrid}genericMessage", &notf, &err)
        || !jw_dom_put_namespace(notf, "", "http://www.cisco.com/pxgrid", &err)
        || !helper_jw_dom_add_child_with_text(notf, "{http://www.cisco.com/pxgrid}capabilityName", capability_name, &err)
        || !helper_jw_dom_add_child_with_text(notf, "{http://www.cisco.com/pxgrid}operationName", operation_name, &err)
        || !helper_jw_dom_add_child_with_text(notf, "{http://www.cisco.com/pxgrid}messageType", "notification", &err)
        || !jw_dom_element_create(ctx, "{http://www.cisco.com/pxgrid}body", &body, &err)
        || !jw_dom_add_child(notf, body, &err)
        || !helper_jw_dom_add_child_with_text(body, "{http://www.cisco.com/pxgrid}content", publish_data, &err)
        )
    {
        jw_log_err(JW_LOG_ERROR, &err, "capability publish error");
        return PXGRID_STATUS_PXGRID_ERROR;
    }
    
    printf("Sent notification\n");
    helper_print_jw_dom(notf);
    
    PXGRID_STATUS status = pxgrid_connection_notify(connection, capability, notf);
    if (status != PXGRID_STATUS_OK) {
        printf("capability publish data status=%d\n", status);
    }
    return status;
}

int main(int argc, char **argv) {
    helper_connection *hconn;
    helper_connection_create(&hconn, argc, argv);
    helper_connection_connect(hconn);
    
    char cap_name[128];
    helper_prompt("Enter capability name for publishing: ", cap_name);
    
    pxgrid_connection *connection = hconn->connection;

    pxgrid_capability *capability;
    pxgrid_capability_create(&capability);
    
    const char pxgrid_ns[] = "http://www.cisco.com/pxgrid";
    pxgrid_dynamic_capability_set_name(capability, cap_name);
    pxgrid_capability_set_namespace(capability, pxgrid_ns);
    pxgrid_dynamic_capability_publish(capability, connection);
    
    char *notification_name = "sampleNotification";
    char capability_publish_data[4096];
    while ((helper_prompt("Publish data (or <enter> to quit): ", capability_publish_data)))  {
       _dynamic_capability_publish_data(connection, capability, cap_name,  notification_name, capability_publish_data);
    }

    helper_connection_disconnect(hconn);
    helper_connection_destroy(hconn);
    
    return 0;
}


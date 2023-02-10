#include <stdlib.h>
#include <unistd.h>
#include <memory.h>
#include "pxgrid.h"
#include "helper.h"

#include <openssl/ssl.h>
#define UNUSED(x) (void)(x)

int _pem_key_password_cb(char *buf, int size, int rwflag, void *userdata) {
    UNUSED(rwflag);
    helper_config *hconfig = userdata;
    strncpy(buf, hconfig->client_cert_key_password, size);
    buf[size - 1] = '\0';
    return (int)strlen(buf);
}

static void _user_ssl_ctx_cb( pxgrid_connection *connection, void *_ssl_ctx, void *user_data ) {
   
    helper_config *hconfig = user_data;
    SSL_CTX *ssl_ctx = _ssl_ctx;
    printf("_user_ssl_ctx_cb calling \n");
    SSL_CTX_set_default_passwd_cb(ssl_ctx, _pem_key_password_cb);
    SSL_CTX_set_default_passwd_cb_userdata(ssl_ctx, hconfig);  
    SSL_CTX_use_certificate_chain_file(ssl_ctx, hconfig->client_cert_chain_filename);
    SSL_CTX_use_PrivateKey_file(ssl_ctx, hconfig->client_cert_key_filename, SSL_FILETYPE_PEM);
    SSL_CTX_load_verify_locations(ssl_ctx, hconfig->server_cert_chain_filename, NULL);    
    SSL_CTX_set_verify(ssl_ctx, SSL_VERIFY_PEER, NULL);   
}

static void _on_disconnected(pxgrid_connection *connection, PXGRID_STATUS status, void *user_data) {
    UNUSED(connection);
    UNUSED(user_data);
	printf("disconnected!!! status=%s\n", pxgrid_status_get_message(status));
}

static void _on_connected(pxgrid_connection *connection, void *user_data) {
   UNUSED(connection);
   UNUSED(user_data);
   printf("wow connected!!!\n");
}


const char change_elname[] = "change";
const char capability_elname[] = "capability";
const char name_elname[] = "name";
const char version_elname[] = "version";
const char description_elname[] = "description";
const char vendorplatform_elname[] = "vendorPlatform";
const char querymethods_elname[] = "queryMethods";
const char operation_elname[] = "operation";
const char methodname_elname[] = "methodName";
const char methodpermissions_elname[] = "methodPermissions";
const char pendingstatus_elname[] = "pendingStatus";
const char topicstatus_elname[] = "topicStatus";
const char status_elname[] = "status";

static void print_first_element_text(jw_dom_node *node, const char *element_name) {
    jw_dom_node *element = jw_dom_get_first_element(node, element_name);
    if (element) {
        const char *text = jw_dom_get_first_text(element);
        if (text) {
            printf("%s=%s, ", element_name, text);
        }
    }
}

static void print_querymethods(jw_dom_node *querymethods_element) {
    jw_dom_node *operation_el = jw_dom_get_first_element(querymethods_element, operation_elname);

    if (operation_el) {
        printf("%s=", operation_elname); 
    }
    
    while (operation_el) {
        jw_dom_node *methodname_el = jw_dom_get_first_element(operation_el, methodname_elname);
        if (methodname_el) {
            const char *method_name = jw_dom_get_first_text(methodname_el);
            if (method_name) {
                printf("%s", method_name);
            }

        }

        jw_dom_node *methodpermissions_el = jw_dom_get_first_element(operation_el, methodpermissions_elname);
        if (methodpermissions_el) {
            const char *method_permission = jw_dom_get_first_text(methodpermissions_el);
            if (method_permission) {
                printf("(%s)", method_permission);
            }
        }

        printf(",");
        operation_el = jw_dom_get_sibling(operation_el);    
    }        
}

static void print_capabilities(jw_dom_node *capability_el) {
    while (capability_el) {
        print_first_element_text(capability_el, name_elname);
        print_first_element_text(capability_el, version_elname);
        print_first_element_text(capability_el, description_elname);
        print_first_element_text(capability_el, vendorplatform_elname);

        jw_dom_node *querymethods_el = jw_dom_get_first_element(capability_el, querymethods_elname);
        if(querymethods_el) {
            print_querymethods(querymethods_el);
        }

        capability_el = jw_dom_get_sibling(capability_el);
        printf("\n\n");
    }
}

static void print_capability_status(jw_dom_node *element) {
    print_first_element_text(element, status_elname);

    jw_dom_node *capability_el = jw_dom_get_first_element(element, capability_elname);
    if (capability_el) {
        print_capabilities(capability_el);
    }
}


static void message_callback(jw_dom_node *node, void *arg) {
    UNUSED(arg);
    printf("Notification - ");
    //helper_print_jw_dom(node);
    print_first_element_text(node, change_elname);
    jw_dom_node *capability_el = jw_dom_get_first_element(node, capability_elname);
    print_capabilities(capability_el);
}

static void get_all_capabilities(pxgrid_connection *connection) {
    PXGRID_STATUS status;

    printf("Registered Capabilities - \n");

    jw_dom_node *response = NULL;
    status = pxgrid_connection_query_capabilities(connection, &response);
    if (PXGRID_STATUS_OK == status) {
        if (NULL != response) {
            //helper_print_jw_dom(response);
            jw_dom_node *capability_el = jw_dom_get_first_element(response, capability_elname);
            print_capabilities(capability_el);

            // Free the response structure.
            jw_dom_context_destroy(jw_dom_get_context(response));
        }
    }
}

static void get_capability_status(pxgrid_connection *connection, const char *name, 
                                                    const char *version) {
    printf("\n");
    PXGRID_STATUS status;

    jw_dom_node *response = NULL;
    status = pxgrid_connection_query_capability_status(connection, name, version, &response);
    if (PXGRID_STATUS_OK == status) {
        if (NULL != response) {
            //helper_print_jw_dom(response);
            jw_dom_node *status_el = jw_dom_get_first_element(response, status_elname);
            if (status_el) {
                jw_dom_node *pendingstatus_el = jw_dom_get_first_element(status_el, pendingstatus_elname);
                if (pendingstatus_el) {
                    printf("%s: ", pendingstatus_elname);
                    print_capability_status(pendingstatus_el);
                }

                jw_dom_node *topicstatus_el = jw_dom_get_first_element(status_el, topicstatus_elname);
                if (topicstatus_el) {
                    printf("%s: ", topicstatus_elname);
                    print_capability_status(topicstatus_el);
                }
            }

            // Free the response structure.
            jw_dom_context_destroy(jw_dom_get_context(response));
        }
    }
}

int main(int argc, char **argv) {
    PXGRID_STATUS status;
    helper_config *hconfig = NULL;
    pxgrid_config *conn_config = NULL;
    pxgrid_connection *connection = NULL;
    helper_config_create(&hconfig, argc, argv); 
    if(!hconfig) 
	{
	    printf("Unable to create hconfig object\n");
		exit(EXIT_FAILURE);
	} 
    helper_pxgrid_config_create(hconfig , &conn_config);
    pxgrid_connection_create( &connection );
     
    // Set connection configuration data
    pxgrid_connection_set_config(connection , conn_config);

    // Set Call back
    pxgrid_connection_set_disconnect_cb(connection, _on_disconnected);	
	pxgrid_connection_set_connect_cb(connection, _on_connected);

    pxgrid_connection_set_ssl_ctx_cb(connection, (pxgrid_connection_ssl_ctx_cb)_user_ssl_ctx_cb);
    pxgrid_connection_set_ssl_ctx_cb_user_data(connection, (helper_config *)hconfig);

	pxgrid_connection_register_topic_notification_handler(connection,  message_callback, NULL);

    pxgrid_connection_connect(connection);

    // Get and print all capabilities using core capability.
    get_all_capabilities(connection);

    char cap_query[128];
    while (helper_prompt("\nCapability name[,version] to query (or <enter> to quit): ", cap_query)) {
        char *cap_name = NULL;
        char *cap_version = NULL;
        char *tf = NULL;

        tf = strtok(cap_query,",");
        cap_name = strdup(tf);
        tf = strtok (NULL,",");	
	if (tf != NULL)
        {	
	    cap_version = strdup(tf);
	}

        // Get and print status for a single capability
        get_capability_status(connection, (const char *) cap_name, (const char *) cap_version);
    }

	//printf("press <enter> to disconnect...\n");
	//getchar();

   	if (connection) {
		pxgrid_connection_disconnect(connection);
		pxgrid_connection_destroy(connection);
	}

	if (conn_config) pxgrid_config_destroy(conn_config);
   	if (hconfig) helper_config_destroy(hconfig);
        return 0;
}


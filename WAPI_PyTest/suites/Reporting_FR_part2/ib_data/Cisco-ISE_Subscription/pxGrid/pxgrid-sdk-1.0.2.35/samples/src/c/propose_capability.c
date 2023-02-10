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

static void print_first_element_text(jw_dom_node *node, const char *element_name) {
    jw_dom_node *element = jw_dom_get_first_element(node, element_name);
    if (element) {
        const char *text = jw_dom_get_first_text(element);
        if (text) {
            printf("%s: %s, ", element_name, text);
        }
    }
}

static void print_capabilities(jw_dom_node *capability_el) {
    while (capability_el) {
        print_first_element_text(capability_el, name_elname);
        print_first_element_text(capability_el, version_elname);

        capability_el = jw_dom_get_sibling(capability_el);
        printf("\n");
    }
    printf("\n");
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

	pxgrid_capability *capability;
	pxgrid_capability_create(&capability);
    if(!capability) exit(EXIT_FAILURE);
    
    const char ns_iden[] = "http://www.cisco.com/pxgrid/core";
	pxgrid_capability_set_namespace(capability, ns_iden);

	const char* cap_name = hconfig->cap_name;
	const char* cap_version = hconfig->cap_version;

	char* tf = NULL;
	char *capquerynames[20];
	int nCapQueries = 0;
	tf = NULL;
	tf = strtok(hconfig->cap_query ,",");	
	while (tf != NULL)
	{
	    capquerynames[nCapQueries] = strdup(tf);	
	    tf = strtok (NULL,",");	 
	    nCapQueries++;
	}

	char *capactionnames[20];
	int nCapActions = 0;
	tf = NULL;
	tf = strtok(hconfig->cap_action ,",");	
	while (tf != NULL)
	{
	    capactionnames[nCapActions] = strdup(tf);	
	    tf = strtok (NULL,",");	 
	    nCapActions++;
	}

	const char* cap_description = hconfig->cap_description;
	const char* cap_vendorplatform = hconfig->cap_vendorplatform;

   	status = pxgrid_capability_propose(capability, connection, cap_name, cap_version, 
					(const char **) capquerynames, nCapQueries, 
					(const char **) capactionnames, nCapActions,
                                        cap_description, cap_vendorplatform);
	if (status != PXGRID_STATUS_OK)
    {
        helper_print_error(status);
    }
	else
	{
		printf("capability: %s create request sent successfully\n", cap_name);	
	}

	printf("press <enter> to disconnect...\n");
	getchar();

   	if (connection) {
		pxgrid_connection_disconnect(connection);
		pxgrid_connection_destroy(connection);
	}

	if (capability) pxgrid_capability_destroy(capability);
	if (conn_config) pxgrid_config_destroy(conn_config);
   	if (hconfig) helper_config_destroy(hconfig);
        return 0;
}


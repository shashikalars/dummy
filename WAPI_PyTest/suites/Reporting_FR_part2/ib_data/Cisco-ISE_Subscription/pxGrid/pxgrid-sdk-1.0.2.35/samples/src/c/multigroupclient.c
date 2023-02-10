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

static void message_callback(jw_dom_node *node, void *arg) {
    UNUSED(arg);
	helper_print_jw_dom(node);
}

static void session_query(pxgrid_connection *connection, pxgrid_capability *capability, char *ip) {
	jw_err err;
	jw_dom_ctx_type *ctx;
	jw_dom_node *request;
	jw_dom_node *ip_interface;
	jw_dom_node *ip_address;
	jw_dom_node *ip_address_text;
	jw_dom_node *response;

    if (!jw_dom_context_create(&ctx, &err)
   		|| !jw_dom_element_create(ctx, "{http://www.cisco.com/pxgrid/identity}getActiveSessionByIPAddressRequest", &request, &err)
   		|| !jw_dom_element_create(ctx, "{http://www.cisco.com/pxgrid/identity}ipInterface", &ip_interface, &err)
    	|| !jw_dom_add_child(request, ip_interface, &err)
   		|| !jw_dom_element_create(ctx, "{http://www.cisco.com/pxgrid}ipAddress", &ip_address, &err)
    	|| !jw_dom_add_child(ip_interface, ip_address, &err)
    	|| !jw_dom_text_create(ctx, ip, &ip_address_text, &err)
    	|| !jw_dom_add_child(ip_address, ip_address_text, &err)
    	)
    {
    	jw_log_err(JW_LOG_ERROR, &err, "query");
    	return;
    }

    PXGRID_STATUS status = pxgrid_connection_query(connection, capability, request, &response);
    if (status == PXGRID_STATUS_OK) {
    	helper_print_jw_dom(response);
        printf("\nSessionDirectory Capability successfully queried\n\n");
    }
    else {
    	printf("\nSessionDirectoryCapability status=%s\n\n", pxgrid_status_get_message(status));
    }
}

static void anc_getAllPolicies(pxgrid_connection *connection, pxgrid_capability *capability) {
    PXGRID_STATUS status = PXGRID_STATUS_OK;
    
    jw_err err;
    jw_dom_ctx_type *ctx;
    jw_dom_node *request;
    jw_dom_node *response;

    /*
    <getAllPoliciesRequest xmlns='http://www.cisco.com/pxgrid/anc'/>
    */

    if (!jw_dom_context_create(&ctx, &err)
        || !jw_dom_element_create(ctx, "{http://www.cisco.com/pxgrid/anc}getAllPoliciesRequest", &request, &err)
        )
    {
        jw_log_err(JW_LOG_ERROR, &err, "ANC query");
        return;
    }

    status = pxgrid_connection_query(connection, capability, request, &response);
    if (status == PXGRID_STATUS_OK) {
    	helper_print_jw_dom(response);
        printf("\nANC Policies successfully queried\n\n");
    }
    else {
    	printf("\nANC getAllPoliciesRequest status=%s\n\n", pxgrid_status_get_message(status));
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

    pxgrid_connection_connect(connection);
	    
	pxgrid_capability *capability;
	pxgrid_capability_create(&capability);
    
    if(!capability) exit(EXIT_FAILURE);
    
    const char ns_iden[] = "http://www.cisco.com/pxgrid/identity";
    const char cap_name[] = "SessionDirectoryCapability";
    
    pxgrid_capability_set_namespace(capability, ns_iden);
    pxgrid_capability_set_name(capability, cap_name);
    pxgrid_capability_subscribe(capability, connection);
    char ip_address[128];
    if (helper_prompt("\nip_address to query (or <enter> to quit): ", ip_address))
    session_query(connection, capability, ip_address);


    pxgrid_capability *anc_capability;
    pxgrid_capability_create(&anc_capability);

    if(!anc_capability) exit(EXIT_FAILURE);
  
    char namespacebuf[] = "http://www.cisco.com/pxgrid/anc";
    char namebuf[] = "AdaptiveNetworkControlCapability";
    
    pxgrid_capability_set_namespace(anc_capability, namespacebuf);
    pxgrid_capability_set_name(anc_capability, namebuf);
    pxgrid_capability_subscribe(anc_capability, connection);
    anc_getAllPolicies(connection, anc_capability);

    //printf("press <enter> to disconnect...\n");
    //getchar();

    if (connection) {
        pxgrid_connection_disconnect(connection);
        pxgrid_connection_destroy(connection);
    }

    if (capability) pxgrid_capability_destroy(capability);
    if (anc_capability) pxgrid_capability_destroy(anc_capability);
    if (conn_config) pxgrid_config_destroy(conn_config);
    if (hconfig) helper_config_destroy(hconfig);
    return 0;
}


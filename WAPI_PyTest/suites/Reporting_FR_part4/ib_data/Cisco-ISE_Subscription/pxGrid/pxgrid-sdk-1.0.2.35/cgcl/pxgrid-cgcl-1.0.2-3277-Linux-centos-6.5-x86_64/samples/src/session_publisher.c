#include <stdlib.h>
#include <unistd.h>
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
 
static bool add_child_and_text(jw_dom_node *parent, const char *child_name, const char *text, jw_err *err) {
	jw_dom_ctx *ctx = jw_dom_get_context(parent);
    jw_dom_node *child_node;
    jw_dom_node_type *child_text;

    if(!jw_dom_element_create(ctx, child_name, &child_node, err)
    	|| !jw_dom_text_create(ctx, text, &child_text, err)
    	|| !jw_dom_add_child(child_node, child_text, err)
    	|| !jw_dom_add_child(parent, child_node, err)
    	)
    {
        jw_log_err(JW_LOG_ERROR, err, "_dom_add_child_and_text");
    	return false;
    }
    return true;
}

static void notification(pxgrid_connection *connection, pxgrid_capability *capability, char *ip) {
	jw_err err;
	jw_dom_ctx_type *ctx;
	jw_dom_node *notf;
	jw_dom_node *sessions;
	jw_dom_node *session;
	jw_dom_node *interface;
	jw_dom_node *ip_interface_id;
	jw_dom_node *user;

    if (!jw_dom_context_create(&ctx, &err)
   		|| !jw_dom_element_create(ctx, "{http://www.cisco.com/pxgrid/identity}sessionNotification", &notf, &err)
    	|| !jw_dom_put_namespace(notf, "", "http://www.cisco.com/pxgrid", &err)
    	|| !jw_dom_put_namespace(notf, "id","http://www.cisco.com/pxgrid/identity", &err)
    	|| !jw_dom_put_namespace(notf, "xgn","http://www.cisco.com/pxgrid/net", &err)
   		|| !jw_dom_element_create(ctx, "{http://www.cisco.com/pxgrid/identity}sessions", &sessions, &err)
    	|| !jw_dom_add_child(notf, sessions, &err)
   		|| !jw_dom_element_create(ctx, "{http://www.cisco.com/pxgrid/identity}session", &session, &err)
    	|| !jw_dom_add_child(sessions, session, &err)
    	|| !add_child_and_text(session, "{http://www.cisco.com/pxgrid}gid", "101", &err)
    	|| !add_child_and_text(session, "{http://www.cisco.com/pxgrid/net}state", "Authenticated", &err)
   		|| !jw_dom_element_create(ctx, "{http://www.cisco.com/pxgrid/net}interface", &interface, &err)
    	|| !jw_dom_add_child(session, interface, &err)
   		|| !jw_dom_element_create(ctx, "{http://www.cisco.com/pxgrid/net}ipIntfID", &ip_interface_id, &err)
    	|| !jw_dom_add_child(interface, ip_interface_id, &err)
    	|| !add_child_and_text(ip_interface_id, "{http://www.cisco.com/pxgrid}ipAddress", ip, &err)
    	|| !add_child_and_text(interface, "{http://www.cisco.com/pxgrid/net}macAddress", "00:11:22:33:44:55", &err)
   		|| !jw_dom_element_create(ctx, "{http://www.cisco.com/pxgrid/net}user", &user, &err)
    	|| !jw_dom_add_child(session, user, &err)
    	|| !add_child_and_text(user, "{http://www.cisco.com/pxgrid}name", "user1", &err)
    	)
    {
    	jw_log_err(JW_LOG_ERROR, &err, "query");
    	return;
    }

    PXGRID_STATUS status = pxgrid_connection_notify(connection, capability, notf);
    if (status != PXGRID_STATUS_OK) {
    	printf("status=%d\n", status);
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
    
    
	pxgrid_capability *capability = NULL;
	pxgrid_capability_create(&capability);
    
    if(!capability) exit(EXIT_FAILURE);
    
    const char ns_iden[] = "http://www.cisco.com/pxgrid/identity";
    const char cap_name[] = "SessionDirectoryCapability";
    
    pxgrid_capability_set_namespace(capability, ns_iden);
	pxgrid_capability_set_name(capability, cap_name);

    
	pxgrid_capability_publish(capability, connection);
	
	/* notification(connection, capability, "10.0.0.2"); */
	printf("------->1.1.18.139\n");
	notification(connection, capability, "1.1.18.139");
	printf("------->1.1.34.84\n");
	notification(connection, capability, "1.1.34.84");
	printf("*** notified\n");

	sleep(600);

	pxgrid_connection_disconnect(connection);
	printf("*** disconnected\n");

	pxgrid_capability_destroy(capability);
	pxgrid_connection_destroy(connection);
    helper_config_destroy(hconfig);
  	return 0;
}


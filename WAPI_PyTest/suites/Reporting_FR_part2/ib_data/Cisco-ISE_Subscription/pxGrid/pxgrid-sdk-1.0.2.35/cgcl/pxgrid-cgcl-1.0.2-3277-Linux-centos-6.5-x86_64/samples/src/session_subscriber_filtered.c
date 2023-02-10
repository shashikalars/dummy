#include <stdlib.h>
#include <unistd.h>
#include <memory.h>
#include "pxgrid.h"
#include "helper.h"
#include <openssl/ssl.h>
#define XGRID_NAMESPACE "{http://www.cisco.com/pxgrid}"
#define XSI_NAMESPACE "{http://www.w3.org/2001/XMLSchema-instance}"

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
 
static void _add_filter_subnet(jw_dom_node *filter_node, char *filter ) {
	jw_err err;
	jw_dom_ctx *ctx = jw_dom_get_context(filter_node);
	jw_dom_node *subnet_node;
	jw_dom_node *network_ip_node;
	jw_dom_node *netmask_node;
	jw_dom_node *text_node;
	jw_dom_element_create(ctx, XGRID_NAMESPACE "subnets", &subnet_node, &err);
	jw_dom_element_create(ctx, XGRID_NAMESPACE "NetworkIp", &network_ip_node, &err);
	jw_dom_element_create(ctx, XGRID_NAMESPACE "Netmask", &netmask_node, &err);

	char *ip = strtok(filter , "/");
	char *netmask = strtok(NULL , "/");	
	jw_dom_text_create(ctx, ip, &text_node, &err);
	jw_dom_add_child(network_ip_node, text_node, &err);

	jw_dom_text_create(ctx, netmask, &text_node, &err);
	jw_dom_add_child(netmask_node, text_node, &err);

	jw_dom_add_child(subnet_node, network_ip_node, &err);
	jw_dom_add_child(subnet_node, netmask_node, &err);
	jw_dom_add_child(filter_node, subnet_node, &err);
}
static void _add_filter(pxgrid_capability *capability , char *_filters) {
	/*
	   <ns2:contentFilter xmlns:ns2="http://www.cisco.com/pxgrid" xsi:type="ns2:SubnetContentFilter">
	    <ns2:subnets>
	      <ns2:NetworkIp>10.1.0.0</ns2:NetworkIp>
      	  <ns2:Netmask>255.255.255.0</ns2:Netmask>
	    </ns2:subnets>
	    <ns2:subnets>
	      <ns2:NetworkIp>10.2.0.0</ns2:NetworkIp>
	      <ns2:Netmask>255.255.255.0</ns2:Netmask>
	    </ns2:subnets>
	   </ns2:contentFilter>
	 */
	jw_dom_ctx *ctx;
	jw_err err;
	jw_dom_node *content_filter_node = NULL;
	jw_dom_context_create(&ctx, &err);
	jw_dom_element_create(ctx, XGRID_NAMESPACE "contentFilter", &content_filter_node, &err);
	jw_dom_put_namespace(content_filter_node, "", "http://www.cisco.com/pxgrid", &err);
	jw_dom_set_attribute(content_filter_node, XSI_NAMESPACE "type", "SubnetContentFilter", &err);
	
	char *filter[20]={0};
	int i =0 ;
	char *tf = NULL;
	tf = strtok(_filters ," ");	
	while (tf != NULL)
	{
	    filter[i] = (char*) calloc(strlen(tf)+1 , sizeof(char));
		strncpy(filter[i] ,tf ,strlen(tf)+1 );	
	    tf = strtok (NULL," ");	 
	    i++;
	}
	
	for(i=i-1;i >= 0;i--)
	{
		_add_filter_subnet(content_filter_node , filter[i]);
	}
	pxgrid_capability_set_filter(capability, content_filter_node);
}

static void message_callback(jw_dom_node *node, void *arg) {
    UNUSED(arg);
    helper_print_jw_dom(node);
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

    _add_filter(capability, hconfig->filter);
    
    const char ns_iden[] = "http://www.cisco.com/pxgrid/identity";
    const char cap_name[] = "SessionDirectoryCapability";
    
    pxgrid_capability_set_namespace(capability, ns_iden);
	pxgrid_capability_set_name(capability, cap_name);

   pxgrid_capability_subscribe(capability, connection);
   
   const char sess_notif[] = "sessionNotification";
   
	pxgrid_connection_register_notification_handler(connection, ns_iden, sess_notif, message_callback, NULL);

    sleep(600);
	
	pxgrid_connection_disconnect(connection);
	printf("*** disconnected\n");

	pxgrid_capability_destroy(capability);
	pxgrid_connection_destroy(connection);
    helper_config_destroy(hconfig);
   	return 0;
}


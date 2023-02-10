/*
 * sessions_download.c
 *
 *  Created on: Sep 12, 2013
 *      Author: lmargali
 */

#include "pxgrid.h"
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <stdbool.h>
#include <jabberwerx/jabberwerx.h>

#include "helper.h"



#define XGRID_NAMESPACE "{http://www.cisco.com/pxgrid}"
#define XSI_NAMESPACE "{http://www.w3.org/2001/XMLSchema-instance}"
#include <openssl/ssl.h>
#define UNUSED(x) (void)(x)
#define REST_ERROR_SIZE 128
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
static void _ssl_ctx_cb(pxgrid_bulkdownload *bulkdownload, void *_ssl_ctx, void *user_data) {
    UNUSED(bulkdownload);
    SSL_CTX *ssl_ctx = _ssl_ctx;
    helper_config *hconfig = user_data;
    printf("_ssl_ctx_cb calling \n");
    SSL_CTX_set_default_passwd_cb(ssl_ctx, _pem_key_password_cb);
    SSL_CTX_set_default_passwd_cb_userdata(ssl_ctx, hconfig);
    SSL_CTX_use_certificate_chain_file(ssl_ctx, hconfig->client_cert_chain_filename);
    SSL_CTX_use_PrivateKey_file(ssl_ctx, hconfig->client_cert_key_filename, SSL_FILETYPE_PEM);
    SSL_CTX_load_verify_locations(ssl_ctx, hconfig->bulk_server_cert_chain_filename, NULL);
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
static void _add_filter_subnet(jw_dom_node *filter_node, char * filter) {
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

static void _add_filter(jw_dom_node *request , char * _filters) {
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
	jw_dom_ctx *ctx = jw_dom_get_context(request);
	jw_err err;
	jw_dom_node *content_filter_node;
	jw_dom_element_create(ctx, "{http://www.cisco.com/pxgrid/identity}contentFilter", &content_filter_node, &err);
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
	
	jw_dom_add_child(request, content_filter_node, &err);
}

static void session_directory_service_query_get_host(pxgrid_connection *connection, char host[], size_t hostsize) { 
	jw_err err;
	jw_dom_ctx_type *ctx;
	jw_dom_node *request;
	jw_dom_node *response = NULL;
	
	/* validate input parameter */
	if(!host) {
		return;
	}
	host[0] = '\0';

	if(hostsize <= 1) {
		return;
	}

	if (!jw_dom_context_create(&ctx, &err) ||
		!jw_dom_element_create(ctx, "{http://www.cisco.com/pxgrid/identity}getSessionDirectoryHostnamesRequest", &request, &err) ||
		!jw_dom_put_namespace(request, "ns2", "http://www.cisco.com/pxgrid", &err) ||
		!jw_dom_put_namespace(request, "ns3", "http://www.cisco.com/pxgrid/net", &err) ||
		!jw_dom_put_namespace(request, "ns4", "http://www.cisco.com/pxgrid/admin", &err) ||
		!jw_dom_put_namespace(request, "ns5", "http://www.cisco.com/pxgrid/identity", &err) ||
		!jw_dom_put_namespace(request, "ns6", "http://www.cisco.com/pxgrid/eps", &err) ||
		!jw_dom_put_namespace(request, "ns7", "http://www.cisco.com/pxgrid/netcap", &err) 
		)
	{
		jw_log_err(JW_LOG_ERROR, &err, "query");
		return;
	}	
	
	pxgrid_capability *capability = NULL; 
	pxgrid_capability_create(&capability);

	char namespacebuf[] = "http://www.cisco.com/pxgrid/identity";
    char namebuf[] = "SessionDirectoryCapability";

	pxgrid_capability_set_namespace(capability, namespacebuf);
	pxgrid_capability_set_name(capability, namebuf);
	pxgrid_capability_subscribe(capability, connection);
	
	
	PXGRID_STATUS status = pxgrid_connection_query(connection, capability, request, &response);
	if (status == PXGRID_STATUS_OK) {
		printf("*** queried\n");
		if(response) {
			jw_dom_node *hostnames_node = jw_dom_get_first_element(response, "hostnames");
			jw_dom_node *hostname_node = jw_dom_get_first_element(hostnames_node, "hostname");
			if(hostname_node) {
				strncpy(host, jw_dom_get_first_text(hostname_node), hostsize - 1);
			}
		}
	}	
	else {
		printf("status=%s\n", pxgrid_status_get_message(status));
	}	
	pxgrid_capability_destroy(capability);
}

static jw_dom_node *_create_request(char * _filters) {
	jw_err err;
	jw_dom_ctx *ctx = NULL;
	jw_dom_node *request = NULL;
	jw_dom_node *time_window;
	jw_dom_node *begin_node, *end_node;
	jw_dom_node	*text_node;

	static char *dateFormat = "%Y-%m-%dT%H:%M:%SZ";
	time_t endTime = time(NULL), beginTime = endTime - 604800;

	char begin_string[50], end_string[50];
	strftime(begin_string, sizeof(begin_string), dateFormat, gmtime(&beginTime));
	strftime(end_string, sizeof(end_string), dateFormat, gmtime(&endTime));

	if (!jw_dom_context_create(&ctx, &err) ||
		!jw_dom_element_create(ctx, "{http://www.cisco.com/pxgrid/identity}getSessionListByTimeRequest", &request, &err) ||
		!jw_dom_put_namespace(request, "ns2", "http://www.cisco.com/pxgrid/identity", &err) ||
		!jw_dom_put_namespace(request, "ns3", "http://www.cisco.com/pxgrid/net", &err) ||
		!jw_dom_put_namespace(request, "", "http://www.cisco.com/pxgrid", &err) ||
		!jw_dom_element_create(ctx, "{http://www.cisco.com/pxgrid/identity}timeWindow", &time_window, &err) ||
		!jw_dom_add_child(request, time_window, &err) ||
		!jw_dom_element_create(ctx, "{http://www.cisco.com/pxgrid}begin", &begin_node, &err) ||
		!jw_dom_add_child(time_window, begin_node, &err) ||
		!jw_dom_text_create(ctx, begin_string, &text_node, &err) ||
		!jw_dom_add_child(begin_node, text_node, &err) ||
		!jw_dom_element_create(ctx, "{http://www.cisco.com/pxgrid}end", &end_node, &err) ||
		!jw_dom_add_child(time_window, end_node, &err) ||
		!jw_dom_text_create(ctx, end_string, &text_node, &err) ||
		!jw_dom_add_child(end_node, text_node, &err)
		)
	{
		jw_log_err(JW_LOG_ERROR, &err, "_create_request()");
	}

	// Add filter
	_add_filter(request , _filters);

	return request;
}



static const char bulkdownload_result_cb_user_data[] = "sessions_download_filtered";

int main(int argc, char *argv[]) {
	PXGRID_STATUS status = PXGRID_STATUS_UNKNOWN;

    pxgrid_connection *connection = NULL;
    pxgrid_config *conn_config = NULL;
    pxgrid_bulkdownload *bulkdownload = NULL;
    jw_dom_node *request = NULL;
    helper_config *hconfig = NULL;
    helper_config_create(&hconfig, argc, argv);
	
	if(!hconfig) 
	{
	    printf("Unable to create hconfig object\n");
		goto cleanup; 
	}
    
    if (hconfig->rest_host == NULL) {
        fprintf(stderr, "Command line option [-r <rest_host>] missing\n");
        exit(EXIT_FAILURE);
    }
	
	if (hconfig->filter == NULL) {
        fprintf(stderr, "Command line option [-f <ipAddress/netmask>] missing\n");
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
    
#define MAX_HOST_SIZE	256    
    char host[MAX_HOST_SIZE] = {0};
    session_directory_service_query_get_host(connection, host, MAX_HOST_SIZE);
    if(!host[0]) 
    {
        printf("Unable to get host name from session directory service\n");
        goto cleanup;
    }

    

    // Bulk download setup
	char url[128];
	sprintf(url, "https://%s/pxgrid/mnt/sd/getSessionListByTime", host);
    
	request = _create_request(hconfig->filter);
    
	pxgrid_config_set_bulk_server_cert_chain_filename(conn_config, hconfig->bulk_server_cert_chain_filename);
    pxgrid_bulkdownload_create(&bulkdownload, conn_config);
	if(!bulkdownload)
	{
		printf("*** bulkdownload Object not created\n");
		goto cleanup;	
	}
	
    pxgrid_bulkdownload_set_url(bulkdownload, url);
    pxgrid_bulkdownload_set_request(bulkdownload, request);
    pxgrid_bulkdownload_set_ssl_ctx_cb(bulkdownload, _ssl_ctx_cb);
    pxgrid_bulkdownload_set_ssl_ctx_cb_user_data(bulkdownload, hconfig);
    
    status = pxgrid_bulkdownload_open(bulkdownload);
	if (status != PXGRID_STATUS_OK)	{
		helper_print_error(status);
		goto cleanup;
	}
    
    printf("*** bulkdownload opened\n");
    
	jw_dom_node *session_node;
	while (true) {
		status = pxgrid_bulkdownload_next(bulkdownload, &session_node);
		if (status != PXGRID_STATUS_OK) break;
       
		if (!session_node) break;
        ise_session *session;
        ise_session_create(&session, session_node);
        ise_session_print(session);
        ise_session_destroy(session);
		jw_dom_context_destroy(jw_dom_get_context(session_node));
	}
    if (status == PXGRID_STATUS_REST_ERROR)
    {
        char desc[REST_ERROR_SIZE] ={0};
        pxgrid_bulkdownload_get_error_details(bulkdownload,desc,REST_ERROR_SIZE);
        printf(" Rest Error[%s]\n",desc);
    }
    else if (status != PXGRID_STATUS_OK)
    {
      helper_print_error(status);
    }
cleanup:
	if (request )
	{
		jw_dom_ctx *ctx = jw_dom_get_context(request);
		if(ctx) jw_dom_context_destroy(ctx);
	}
    if (bulkdownload) {
        pxgrid_bulkdownload_close(bulkdownload);
        pxgrid_bulkdownload_destroy(&bulkdownload);
    }
    printf("*** bulkdownload closed\n");

	if (connection) {
		pxgrid_connection_disconnect(connection);
		pxgrid_connection_destroy(connection);
	}
    printf("*** disconnected\n");

	if (conn_config) pxgrid_config_destroy(conn_config);
    if (hconfig) helper_config_destroy(hconfig);
    return 0;
}

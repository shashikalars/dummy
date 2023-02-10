/*
 * sessions_download.c
 */

#include "pxgrid.h"
#include "helper.h"
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <stdbool.h>
#include <jabberwerx/jabberwerx.h>
#include <openssl/ssl.h>

#define UNUSED(x) (void)(x)
#define REST_ERROR_SIZE 128

static void session_directory_service_query_get_host(pxgrid_connection *connection, char host[], size_t hostsize) { 
	jw_err err;
	jw_dom_ctx_type *ctx = NULL;
	jw_dom_node *request = NULL;
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
    
    char ns[] = "http://www.cisco.com/pxgrid/identity";
    char name[] = "SessionDirectoryCapability";
    
	pxgrid_capability_set_namespace(capability, ns);
	pxgrid_capability_set_name(capability, name);
    
    
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

static jw_dom_node *_create_request() {
	jw_err err;
	jw_dom_ctx *ctx = NULL;
	jw_dom_node *request;
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
		!jw_dom_put_namespace(request, "ns4", "http://www.cisco.com/pxgrid", &err) ||
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
        return NULL;
	}
	return request;
}

int _pem_password_cb(char *buf, int size, int rwflag, void *userdata) {
    UNUSED(rwflag);
    helper_config *hconfig = userdata;
    strncpy(buf, hconfig->client_cert_key_password, size);
    buf[size - 1] = '\0';
    return (int)strlen(buf);
}

static void _ssl_ctx_cb(pxgrid_bulkdownload *bulkdownload, void *_ssl_ctx, void *user_data) {
    UNUSED(bulkdownload);
    SSL_CTX *ssl_ctx = _ssl_ctx;
    helper_config *hconfig = user_data;
    SSL_CTX_set_default_passwd_cb(ssl_ctx, _pem_password_cb);
    SSL_CTX_set_default_passwd_cb_userdata(ssl_ctx, hconfig);
    SSL_CTX_use_certificate_chain_file(ssl_ctx, hconfig->client_cert_chain_filename);
    SSL_CTX_use_PrivateKey_file(ssl_ctx, hconfig->client_cert_key_filename, SSL_FILETYPE_PEM);
    SSL_CTX_load_verify_locations(ssl_ctx, hconfig->bulk_server_cert_chain_filename, NULL);
    SSL_CTX_set_verify(ssl_ctx, SSL_VERIFY_PEER, NULL);
}



static void _user_ssl_ctx_cb( pxgrid_connection *connection, void *_ssl_ctx, void *user_data ) {
   
    helper_config *hconfig = user_data;
    SSL_CTX *ssl_ctx = _ssl_ctx;
    printf("_user_ssl_ctx_cb calling \n");
    SSL_CTX_set_default_passwd_cb(ssl_ctx, _pem_password_cb);
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
 //static const char bulkdownload_result_cb_user_data[] = "sessions_download_filtered";
 
int _on_log_cb(const char * format, va_list ap)
{
    int written = -1;
	char buffer[1024]={0};
	written = vsnprintf(buffer, 1023,format, ap);
   	FILE *fd = fopen("pxg_sample.log", "a+");
	if (fd != NULL)
	{
		fprintf(fd,"%s",buffer);
		fflush(fd);
	}
	fclose(fd);	
    return written;	
}


int main(int argc, char *argv[]) {
   PXGRID_STATUS status;
    helper_config *hconfig = NULL;
    pxgrid_config *conn_config = NULL;
    pxgrid_bulkdownload  *bulkdownload = NULL;
    pxgrid_connection *connection = NULL;
    bool bulkDownloadEverConnected = false;
    
    
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

	pxgrid_log_set_callback(_on_log_cb);
	pxgrid_log_set_level(PXGRID_LOG_VERBOSE);

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

	jw_dom_node * request = _create_request();
    pxgrid_config_set_bulk_server_cert_chain_filename(conn_config , hconfig->bulk_server_cert_chain_filename );
    
    
    pxgrid_bulkdownload_create(&bulkdownload, conn_config);
	if(!bulkdownload) 
	{
	    printf("Unable to create bulkdownload object\n");
		goto cleanup; 
	}
    pxgrid_bulkdownload_set_url(bulkdownload, url);
    pxgrid_bulkdownload_set_request(bulkdownload, request);
    pxgrid_bulkdownload_set_ssl_ctx_cb(bulkdownload, _ssl_ctx_cb);
    pxgrid_bulkdownload_set_ssl_ctx_cb_user_data(bulkdownload, hconfig);
    //pxgrid_bulkdownload_set_open_result_cb(bulkdownload, helper_pxgrid_bulkdownload_open_result_cb);
   // pxgrid_bulkdownload_set_open_result_cb_user_data(bulkdownload, (void*)&bulkDownloadEverConnected);
    status = pxgrid_bulkdownload_open(bulkdownload);
	if (status != PXGRID_STATUS_OK)	
    {
		helper_print_error(status);
		goto cleanup;
	}
    printf("*** bulkdownload opened\n");

	jw_dom_node *session_node = NULL;
	while (true) 
    {
		status = pxgrid_bulkdownload_next(bulkdownload, &session_node);
		
        if (status != PXGRID_STATUS_OK) break;
        if (!session_node) break;
        ise_session *session = NULL;
        ise_session_create(&session, session_node);
        ise_session_print(session);
        ise_session_destroy(session);
		jw_dom_context_destroy(jw_dom_get_context(session_node));
        session_node = NULL;
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

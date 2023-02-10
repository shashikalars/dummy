#include <stdlib.h>
#include <unistd.h>

#include <signal.h>

#include "pxgrid.h"
#include "helper.h"
#include <openssl/ssl.h>
#define UNUSED(x) (void)(x)
/** Enumeration of EPS mitigation action types. */
typedef enum
{
	/**  exclusive lower bound */
	EPS_MA_MIN = 0,
	EPS_MA_QUARANTINE,
	EPS_MA_UNQUARANTINE,
#if 0
	EPS_MA_SHUTDOWN,
	EPS_MA_TERMINATE,
	EPS_MA_REAUTHENTICATE,
	EPS_MA_PORT_BOUNCE,
#endif
	/**  exclusive upper bound */
	EPS_MA_MAX
} eps_mitigation_action_type;

/** Enumeration of EPS mitigation action by. */
typedef enum
{
	/**  exclusive lower bound */
	EPS_MA_BY_MIN = 0,
	EPS_MA_BY_IP,
	EPS_MA_BY_MAC,
#if 0
	EPS_MA_BY_SESSION_ID,
#endif
	/**  exclusive upper bound */
	EPS_MA_BY_MAX
} eps_mitigation_action_by;

static int		gExitFlag		= 0;
static int		isSigKill		= 0;
static int		isSigTerm		= 0;


void signalHandler(int sig)
{
    switch (sig)
    {
          case SIGKILL:
              isSigKill = 1;
              break;
          case SIGTERM:
              isSigTerm = 1;
              break;
          default:
            break;
    }
    if((1 == isSigKill)||(1 == isSigTerm)) {
        gExitFlag = 1;
    }

}


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
 static void tls_failure_cb(pxgrid_connection *connection , void *user_data)
 {
    UNUSED(connection);
    printf("Invalid tls certificate presented!!!\n");
 }

static void message_callback(jw_dom_node *node, void *arg) {
    UNUSED(arg);
	helper_print_jw_dom(node);
}

static void mitigation_action_by_ip(pxgrid_connection *connection, pxgrid_capability *capability, eps_mitigation_action_type action_type, char *ip)
{
	jw_err err;
	jw_dom_ctx_type *ctx;
	jw_dom_node *request;
	jw_dom_node *mitigation_action_node;
	jw_dom_node *mitigation_action_text_node; 
	jw_dom_node *ip_interface_node;
	jw_dom_node *ip_address_node;
	jw_dom_node *ip_address_text_node;
	jw_dom_node *response = NULL;
	
	char action_text[256] = {0};
	
	/* validate input parameter */
	if(!ip) {
		return;
	}

	switch (action_type)
	{    
		 case EPS_MA_QUARANTINE:
			sprintf(action_text, "%s", "quarantine");
			break;

		case EPS_MA_UNQUARANTINE:
			sprintf(action_text, "%s", "unquarantine");
			break;
            
		default:
			break;
	}

	if (!jw_dom_context_create(&ctx, &err) ||
		!jw_dom_element_create(ctx, "{http://www.cisco.com/pxgrid/eps}sendMitigationActionByIPRequest", &request, &err) ||
		!jw_dom_put_namespace(request, "ns2", "http://www.cisco.com/pxgrid", &err) ||
		!jw_dom_put_namespace(request, "ns3", "http://www.cisco.com/pxgrid/net", &err) ||
		!jw_dom_put_namespace(request, "ns4", "http://www.cisco.com/pxgrid/admin", &err) ||
		!jw_dom_put_namespace(request, "ns5", "http://www.cisco.com/pxgrid/identity", &err) ||
		!jw_dom_put_namespace(request, "ns6", "http://www.cisco.com/pxgrid/eps", &err) ||
		!jw_dom_put_namespace(request, "ns7", "http://www.cisco.com/pxgrid/netcap", &err) ||
		!jw_dom_element_create(ctx, "{http://www.cisco.com/pxgrid/eps}mitigationAction", &mitigation_action_node, &err) ||
		!jw_dom_add_child(request, mitigation_action_node, &err) ||
		!jw_dom_text_create(ctx, action_text, &mitigation_action_text_node, &err) ||
		!jw_dom_add_child(mitigation_action_node, mitigation_action_text_node, &err) || 
   		!jw_dom_element_create(ctx, "{http://www.cisco.com/pxgrid/eps}ipInterface", &ip_interface_node, &err) ||
		!jw_dom_add_child(request, ip_interface_node, &err) ||
		!jw_dom_element_create(ctx, "{http://www.cisco.com/pxgrid}ipAddress", &ip_address_node, &err) ||
		!jw_dom_add_child(ip_interface_node, ip_address_node, &err) ||
		!jw_dom_text_create(ctx, ip, &ip_address_text_node, &err) ||
		!jw_dom_add_child(ip_address_node, ip_address_text_node, &err)
		)
	{
		jw_log_err(JW_LOG_ERROR, &err, "mitigation_action_by_ip");
		return;
	}	
	printf("*** request\n");
	helper_print_jw_dom(request);
	
	PXGRID_STATUS status = pxgrid_connection_query(connection, capability, request, &response);
	if (status == PXGRID_STATUS_OK) {
		printf("*** response\n");
		helper_print_jw_dom(response);	
		printf("*** queried\n");
	}	
	else {
		printf("status=%s\n", pxgrid_status_get_message(status));
	}	
} 

static void mitigation_action_by_mac(pxgrid_connection *connection, pxgrid_capability *capability, eps_mitigation_action_type action_type, char *mac)
{
	jw_err err;
	jw_dom_ctx_type *ctx;
	jw_dom_node *request;
	jw_dom_node *mitigation_action_node;
	jw_dom_node *mitigation_action_text_node; 
	jw_dom_node *mac_interface_node;
	jw_dom_node *mac_address_text_node;
	jw_dom_node *response = NULL;
	
	char action_text[256] = {0};
	
	/* validate input parameter */
	if(!mac) {
		return;
	}

	switch (action_type)
	{    
		 case EPS_MA_QUARANTINE:
			sprintf(action_text, "%s", "quarantine");
			break;

		case EPS_MA_UNQUARANTINE:
			sprintf(action_text, "%s", "unquarantine");
			break;
            
		default:
			break;
	}

	if (!jw_dom_context_create(&ctx, &err) ||
		!jw_dom_element_create(ctx, "{http://www.cisco.com/pxgrid/eps}sendMitigationActionByMACRequest", &request, &err) ||
		!jw_dom_put_namespace(request, "ns2", "http://www.cisco.com/pxgrid", &err) ||
		!jw_dom_put_namespace(request, "ns3", "http://www.cisco.com/pxgrid/net", &err) ||
		!jw_dom_put_namespace(request, "ns4", "http://www.cisco.com/pxgrid/admin", &err) ||
		!jw_dom_put_namespace(request, "ns5", "http://www.cisco.com/pxgrid/identity", &err) ||
		!jw_dom_put_namespace(request, "ns6", "http://www.cisco.com/pxgrid/eps", &err) ||
		!jw_dom_put_namespace(request, "ns7", "http://www.cisco.com/pxgrid/netcap", &err) ||
		!jw_dom_element_create(ctx, "{http://www.cisco.com/pxgrid/eps}mitigationAction", &mitigation_action_node, &err) ||
		!jw_dom_add_child(request, mitigation_action_node, &err) ||
		!jw_dom_text_create(ctx, action_text, &mitigation_action_text_node, &err) ||
		!jw_dom_add_child(mitigation_action_node, mitigation_action_text_node, &err) || 
   		!jw_dom_element_create(ctx, "{http://www.cisco.com/pxgrid/eps}macInterface", &mac_interface_node, &err) ||
		!jw_dom_add_child(request, mac_interface_node, &err) ||
		!jw_dom_text_create(ctx, mac, &mac_address_text_node, &err) ||
		!jw_dom_add_child(mac_interface_node, mac_address_text_node, &err)
		)
	{
		jw_log_err(JW_LOG_ERROR, &err, "mitigation_action_by_mac");
		return;
	}	
	printf("*** request\n");
	helper_print_jw_dom(request);
	
	PXGRID_STATUS status = pxgrid_connection_query(connection, capability, request, &response);
	if (status == PXGRID_STATUS_OK) {
		printf("*** response\n");
		helper_print_jw_dom(response);
		printf("*** queried\n");
	}	
	else {
		printf("status=%s\n", pxgrid_status_get_message(status));
	}	
} 

static void eps_service_do_mitigation_action(pxgrid_connection *connection, pxgrid_capability *capability, eps_mitigation_action_type action_type, eps_mitigation_action_by action_by, void *input_data)
{
	switch (action_by)
	{    
		 case EPS_MA_BY_IP:
			mitigation_action_by_ip(connection, capability, action_type, input_data);
			break;

		case EPS_MA_BY_MAC:
			mitigation_action_by_mac(connection, capability, action_type, input_data);
			break;
		default:
			break;
	}

}

#define MIN_FIELD_WIDTH_NUM			2
#define MIN_FIELD_WIDTH_ACTION_STR		32

/* action */
static void cli_print_mitigation_action_usage( )
{
	int bytes_written;
	printf ("\n\n|*************************************************|\n");
	printf ("|%n\t'%-*s'\t'%-*s'|\n", &bytes_written, MIN_FIELD_WIDTH_NUM,"NU", MIN_FIELD_WIDTH_ACTION_STR,"EPS ACTION");
	printf ("|*************************************************|\n");
	printf ("\t[%0*d]\t'%-*s'\n", MIN_FIELD_WIDTH_NUM,EPS_MA_QUARANTINE, MIN_FIELD_WIDTH_ACTION_STR,"EPS_MA_QUARANTINE");
	printf ("\t[%0*d]\t'%-*s'\n", MIN_FIELD_WIDTH_NUM,EPS_MA_UNQUARANTINE, MIN_FIELD_WIDTH_ACTION_STR,"EPS_MA_UNQUARANTINE");
	printf ("|*************************************************|\n");
	printf ("Enter EPS mitigation action [number]: ");
	fflush(stdout);
}

static unsigned int cli_get_mitigation_action_number( )
{
	char			act_num_str[16]			= {0};
	char			act_num_extra_str[16]		= {0};
	unsigned int		act_num				= EPS_MA_MIN; /* invalid value */
	int			act_done			= 0;
	do {
		memset(act_num_str, 0, sizeof(act_num_str));
		memset(act_num_extra_str, 0, sizeof(act_num_extra_str));
		
		cli_print_mitigation_action_usage();
		while ( fgets( act_num_str, sizeof(act_num_str), stdin ) != NULL )
		{
			if ( sscanf( act_num_str, "%i%[^\n]", &act_num, act_num_extra_str ) == 1 ) {
				/* validate */
				if((act_num > EPS_MA_MIN) && (act_num < EPS_MA_MAX)) {
					act_done = 1;
					break;
				}
			}
			/* Do some sort of error processing. */
			fprintf( stdout, "\nError reading EPS mitigation action number[%d]['%s'][act_done=%d], please try again.\n", act_num, act_num_str, act_done);
			act_num = EPS_MA_MIN;
			memset(act_num_str, 0, sizeof(act_num_str));
			memset(act_num_extra_str, 0, sizeof(act_num_extra_str));
			cli_print_mitigation_action_usage();
		}
	} while(0 == act_done);
	return act_num;
}

/* action by */
static void cli_print_mitigation_action_by_usage( )
{
	int bytes_written;
	printf ("\n\n|*************************************************|\n");
	printf ("|%n\t'%-*s'\t'%-*s'|\n", &bytes_written, MIN_FIELD_WIDTH_NUM,"NU", MIN_FIELD_WIDTH_ACTION_STR,"EPS ACTION BY");
	printf ("|*************************************************|\n");
	printf ("\t[%0*d]\t'%-*s'\n", MIN_FIELD_WIDTH_NUM,EPS_MA_BY_IP, MIN_FIELD_WIDTH_ACTION_STR,"EPS_MA_BY_IP");
	printf ("\t[%0*d]\t'%-*s'\n", MIN_FIELD_WIDTH_NUM,EPS_MA_BY_MAC, MIN_FIELD_WIDTH_ACTION_STR,"EPS_MA_BY_MAC");
	printf ("|*************************************************|\n");
	printf ("Enter EPS mitigation action by[number]: ");
	fflush(stdout);
}

static unsigned int cli_get_mitigation_action_by_number( )
{
	char			actby_num_str[16]			= {0};
	char			actby_num_extra_str[16]			= {0};
	unsigned int		actby_num				= EPS_MA_BY_MIN; /* invalid value */
	int			actby_done				= 0;
	do {
		memset(actby_num_str, 0, sizeof(actby_num_str));
		memset(actby_num_extra_str, 0, sizeof(actby_num_extra_str));
		
		cli_print_mitigation_action_by_usage();
		while ( fgets( actby_num_str, sizeof(actby_num_str), stdin ) != NULL )
		{
			if ( sscanf( actby_num_str, "%i%[^\n]", &actby_num, actby_num_extra_str ) == 1 ) {
				/* validate */
				if((actby_num > EPS_MA_BY_MIN) && (actby_num < EPS_MA_BY_MAX)) {
					actby_done = 1;
					break;
				}
			}
			/* Do some sort of error processing. */
			fprintf( stdout, "\nError reading EPS mitigation action by number[%d]['%s'][actby_done=%d], please try again.\n", actby_num, actby_num_str, actby_done);
			actby_num = EPS_MA_BY_MIN;
			memset(actby_num_str, 0, sizeof(actby_num_str));
			memset(actby_num_extra_str, 0, sizeof(actby_num_extra_str));
			cli_print_mitigation_action_by_usage();
		}
	} while(0 == actby_done);
	return actby_num;
}

int main(int argc, char **argv)
{
    
	PXGRID_STATUS 		status 			= PXGRID_STATUS_OK;
	pxgrid_connection	*connection		= NULL;
	pxgrid_config		*conn_config			= NULL;
	helper_config		*hconfig		= NULL;
	
	helper_config_create(&hconfig, argc, argv);
	if(!hconfig) 
	{
	    printf("Unable to create hconfig object\n");
       	exit(EXIT_FAILURE); 
	} 
    helper_pxgrid_config_create(hconfig , &conn_config);
	pxgrid_config_set_user_group(conn_config, "EPS");
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

    char namespacebuf[] = "http://www.cisco.com/pxgrid/eps";
    char namebuf[] = "EndpointProtectionServiceCapability";

	pxgrid_capability_set_namespace(capability, namespacebuf);
	pxgrid_capability_set_name(capability, namebuf);
	
	status = pxgrid_capability_subscribe(capability, connection);
	if (PXGRID_STATUS_OK != status) {
		printf("status=%s\n", pxgrid_status_get_message(status));
	}	

	unsigned int		act_num				= EPS_MA_MIN;		/* invalid value */
	unsigned int		act_by_num			= EPS_MA_BY_MIN;	/* invalid value */
	char			input_data_str[512]		= {0};
	char			input_data[256]			= {0};
	char			input_data_extra_str[256]	= {0};

	do
	{
		act_num				= EPS_MA_MIN;		/* invalid value */
		act_num = cli_get_mitigation_action_number();
		act_by_num			= EPS_MA_BY_MIN;	/* invalid value */
		act_by_num = cli_get_mitigation_action_by_number();
		switch (act_by_num)
		{    
			 case EPS_MA_BY_IP:
				printf ("Enter Endpoint IP address: ");
				fflush(stdout);
				break;

			case EPS_MA_BY_MAC:
				printf ("Enter Endpoint MAC address: ");
				fflush(stdout);
				break;
			default:
				break;
		}

		memset(input_data, 0, sizeof(input_data));
		memset(input_data_extra_str, 0, sizeof(input_data_extra_str));
		while ( fgets( input_data_str, sizeof(input_data_str), stdin ) != NULL )
		{
			if ( sscanf( input_data_str, "%s%[^\n]", input_data, input_data_extra_str ) == 1 ) {
				break;
			}
			/* Do some sort of error processing */
			fprintf( stdout, "\nError reading input data['%s']['%s'], please try again.\n", input_data, input_data_extra_str);
			fflush(stdout);
			memset(input_data, 0, sizeof(input_data));
			memset(input_data_extra_str, 0, sizeof(input_data_extra_str));
		}
		eps_service_do_mitigation_action(connection, capability, (eps_mitigation_action_type)act_num, (eps_mitigation_action_by)act_by_num, input_data);
	}while(1 != gExitFlag);
	
	pxgrid_connection_disconnect(connection);
	printf("*** disconnected\n");

	pxgrid_capability_destroy(capability);
	pxgrid_connection_destroy(connection);
	pxgrid_config_destroy(conn_config);
	helper_config_destroy(hconfig);
    return 0;
}


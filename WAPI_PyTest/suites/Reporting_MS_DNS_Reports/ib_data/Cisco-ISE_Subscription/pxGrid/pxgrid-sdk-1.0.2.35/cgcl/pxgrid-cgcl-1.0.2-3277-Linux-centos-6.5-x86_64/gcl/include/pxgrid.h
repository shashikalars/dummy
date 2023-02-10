/**
 * @mainpage pxGrid Connection Library
 *
 * This is the pxGrid Connection Library.
 * It contains all necessary functions to interact with pxGrid.
 * Since this is a general library that works with any device,
 * it is necessary to manipulate XML via jw_dom_* functions.
 *
 * Start by populating pxgrid_config structure with pxgrid_config_* functions.
 * Then, connect and send messages with pxgrid_connection_* functions.
 *
 * The memory for any jw_dom node passed out should be freed by the calling function. 
 * Callback functions must take ownership of freeing the provided jw_dom node.
 */

/**
 * @file pxgrid.h
 * @brief Functions for pxGrid
 *
 * This contains the function prototypes to perform
 * all functionalities in pxGrid
 *
 * @author Alan Lei
 *
 * @copyright
 *   Copyright (c) 2014 Cisco Systems, Inc.
 *   All rights reserved.
 */

#ifndef PXGRID_H_
#define PXGRID_H_

#include <stdbool.h>
#include <jabberwerx/jabberwerx.h>
#include <time.h>




#ifdef __cplusplus
extern "C" {
#endif

/**
 * Different return codes
 */
typedef enum {
    PXGRID_STATUS_OK = 0, ///< Everything is OK
    PXGRID_STATUS_MALLOC_ERROR, ///< Memory allocation error
    PXGRID_STATUS_XML_ERROR, ///< XML parsing error
    PXGRID_STATUS_JW_ERROR, ///< Underlying Jabberwerx API error
    PXGRID_STATUS_EVENT_ERROR, ///< Underlying Jabberwerx API event error
    PXGRID_STATUS_XMPP_ERROR, ///< XMPP protocol error
    PXGRID_STATUS_REST_ERROR, ///< REST call error
    PXGRID_STATUS_PXGRID_ERROR, ///< General pxGrid error
    PXGRID_STATUS_PTHREAD_ERROR, ///< pthread error
    PXGRID_STATUS_CONNECTION_ERROR, ///< Connection error
    PXGRID_STATUS_CONNECTION_TIMEOUT, ///< Connection timeout
    PXGRID_STATUS_CONNECTION_DENIED, ///< Connection denied. Possibly unauthorized.
    PXGRID_STATUS_ACCOUNT_PENDING, ///< Account pending for approval
    PXGRID_STATUS_ACCOUNT_ENABLED, ///< Account enabled
    PXGRID_STATUS_ACCOUNT_DISABLED, ///< Account disabled
    PXGRID_STATUS_ACCOUNT_DELETED, ///< Acount deleted
    PXGRID_STATUS_ACCOUNT_AUTHORIZATION_CHANGED, ///< Account authorization changed. For example, group assignment changed
    PXGRID_STATUS_SEND_ERROR, ///< Send error
    PXGRID_STATUS_SEND_TIMEOUT, ///< Send timeout
    PXGRID_STATUS_CAPABILITY_NOT_FOUND, ///< Capability not found in pxGrid
    PXGRID_STATUS_NOT_AUTHORIZED, ///< Not authorized
    PXGRID_STATUS_NOT_SUPPORTED, ///< Not supported
    PXGRID_STATUS_UNKNOWN, ///< Unknown
    PXGRID_STATUS_INVALID_ARGS,   ///< function's argument are no valid
    PXGRID_STATUS_REST_INIT_ERROR,  ///< Curl_easy_init failure
    PXGRID_STATUS_CONNECTION_ERROR_HOST, ///< Host issue
    PXGRID_STATUS_CONNECTION_ERROR_CLIENT, ///< Incorrect client credentials
    PXGRID_STATUS_CONNECTION_ERROR_SERVER, ///< Incorrect server credentials
    PXGRID_STATUS_CONNECTION_ERROR_AUTOREGOFF, ///< Registration not authorized
    PXGRID_STATUS_CONNECTION_ERROR_REMOTE_CONNECTION_FAILURE, ///< Remote connection failure
    PXGRID_STATUS_CONNECTION_ERROR_NOT_AUTHORIZED, ///< Not authorized for connection
    PXGRID_STATUS_CONNECTION_ERROR_XMPP, ///< Unknown XMPP error during connection
    PXGRID_STATUS_PROPOSE_CAPABILITY_ERROR, ///< Propose capability error
    PXGRID_STATUS_MODIFY_CAPABILITY_ERROR, ///< Modify capability error
    PXGRID_STATUS_NO_CONNECTION, ///< Connection not established
    PXGRID_STATUS_MAX
} PXGRID_STATUS;



typedef enum
{
	PXGRID_LOG_NONE = 0,
	PXGRID_LOG_ERROR,
	PXGRID_LOG_WARN,
	PXGRID_LOG_INFO,
	PXGRID_LOG_VERBOSE,
	PXGRID_LOG_DEBUG
} PXGRID_LOG_LEVEL;


/**
 * x is char array representing null terminated string
 */
#define CHAR_ARRAY_STRLEN(x)	(sizeof((x)) -1)

/**
 * Default send timeout in seconds
 */
#define PXGRID_CONFIG_SEND_TIME_DEFAULT 15

typedef struct _pxgrid_config pxgrid_config;
typedef struct _pxgrid_connection pxgrid_connection;
typedef struct _pxgrid_reconnection pxgrid_reconnection;
typedef struct _pxgrid_capability pxgrid_capability;

// Connections callbacks
typedef void (*pxgrid_notification_cb)(jw_dom_node *node, void *arg);
typedef jw_dom_node *(*pxgrid_query_cb)(jw_dom_node *request, void *arg);
typedef void (*pxgrid_connection_disconnect_cb)(pxgrid_connection *connection, PXGRID_STATUS status, void *user_data);
typedef void (*pxgrid_connection_connect_cb)(pxgrid_connection *connection, void *user_data);
typedef void (*pxgrid_connection_account_cb)(pxgrid_connection *connection, PXGRID_STATUS status, void *user_data);

typedef void (*pxgrid_connection_ssl_ctx_cb)(pxgrid_connection *connection, void *ssl_ctx, void *user_data);


typedef int (*pxgrid_log_cb)(const char * format , va_list ap);



/**
 * To initialize the pxgrid library.
 * This function must be called only once in a application life time.
 * also this must be called before any other pxgrid api. 
 * @return ::PXGRID_STATUS
 */
 
//PXGRID_STATUS pxgrid_init();
/**
 * To clean up the pxgrid library.
 * This function must be called once in a application life time. 
 * also this api must be call at the end of application.  
 * @return ::PXGRID_STATUS
 */
//PXGRID_STATUS pxgrid_shutdown();
/**
 * Create a pxGrid connection.
 * After use, ::pxgrid_connection_destroy must be called to free up resources
 *
 * @param connection The pointer where the newly created connection structure will be placed
 * @return ::PXGRID_STATUS
 */
PXGRID_STATUS pxgrid_connection_create(pxgrid_connection **connection);

/**
 * Destroy a pxGrid connection
 *
 * @param connection The connection structure
 * @return ::PXGRID_STATUS
 */
PXGRID_STATUS pxgrid_connection_destroy(pxgrid_connection *connection);
    
/**
 * Apply configuration to connection
 * This must set before connecting.
 *
 * @param connection The connection structure
 * @return ::PXGRID_STATUS
 */
PXGRID_STATUS pxgrid_connection_set_config(pxgrid_connection *connection, pxgrid_config *config);
    
/**
 * Connect to pxGrid
 * Can be called again if disconnected
 *
 * If a connection already exists and a second connection is initiated
 * with the same credentials, it will be honored and
 * the first connection will be disconnected because pxgrid server considers it a conflict.
 *
 * @param connection The connection structure
 * @return ::PXGRID_STATUS
 */
PXGRID_STATUS pxgrid_connection_connect(pxgrid_connection *connection);

/**
 * Disconnect from pxGrid
 *
 * @param connection The connection structure
 * @return ::PXGRID_STATUS
 */
PXGRID_STATUS pxgrid_connection_disconnect(pxgrid_connection *connection);

/**
 * Check if connected
 *
 * @param connection The connection structure
 * @return True if connected, otherwise false
 */
bool pxgrid_connection_is_connected(pxgrid_connection *connection);

/**
 * Make a query
 *
 * @param connection The connection structure
 * @param capability The capability to query from
 * @param request The xml for the request payload
 * @param response The pointer where xml response will be written
 * @return ::PXGRID_STATUS
 *
 * If pxgrid_connection_query() returns a valid (not null) response object,
 * the caller function must take ownership of freeing the OUT jw_dom_node. 
 */
PXGRID_STATUS pxgrid_connection_query(pxgrid_connection *connection, pxgrid_capability *capability, jw_dom_node *request, jw_dom_node **response);


/**
 * Make a query directed to pxGrid controller
 *
 * @param connection The connection structure
 * @param request The xml for the request payload
 * @param response The pointer where xml response will be written
 * @return ::PXGRID_STATUS
 *
 * If pxgrid_connection_query_controller() returns a valid (not null) response object,
 * the caller function must take ownership of freeing the OUT jw_dom_node.
 */
PXGRID_STATUS pxgrid_connection_query_controller(pxgrid_connection *connection, jw_dom_node *request, jw_dom_node **response);

/**
 * Query for list of all registered and enabled capabilities.
 *
 * @param connection The connection structure
 * @param response The pointer where xml response will be written
 * @return ::PXGRID_STATUS
 *
 * If pxgrid_connection_query_capabilities() returns a valid (not null) response object,
 * the caller function must take ownership of freeing the OUT jw_dom_node.
 */
PXGRID_STATUS pxgrid_connection_query_capabilities(pxgrid_connection *connection, jw_dom_node **response);

/**
 * Query for capability status (enabled and pending).
 *
 * @param connection The connection structure
 * @param name The capability name
 * @param version The capability version (can be NULL)
 * @param response The pointer where xml response will be written
 * @return ::PXGRID_STATUS
 *
 * If pxgrid_connection_query_capabilities() returns a valid (not null) response object,
 * the caller function must take ownership of freeing the OUT jw_dom_node.
 */
PXGRID_STATUS pxgrid_connection_query_capability_status(pxgrid_connection *connection, const char *name, const char *version, jw_dom_node **response);

/**
 * Register a handler for notification
 *
 * @param connection The connection structure
 * @param ns Namespace of the notification to handle
 * @param name Element name of the notification to handle
 * @param callback The function to callback when a notification is received
 * @param user_data User defined data to be passed to callback
 * @return ::PXGRID_STATUS
 *
 * pxgrid_connection_register_notification_handler() accepts a callback. 
 * The callback must take ownership of freeing the provided jw_dom_node.
 */
PXGRID_STATUS pxgrid_connection_register_notification_handler(pxgrid_connection *connection, const char *ns, const char *name, pxgrid_notification_cb callback, void *user_data);

/**
 * Register a handler to be notified of topic change notifications.
 *
 * @param connection The connection structure
 * @param callback Function to call when a topic change notification is received.
 * @param arg User defined data to be passed to callback
 * @return ::PXGRID_STATUS
 *
 * @note pxgrid_connection_register_topic_notification_handler() accepts a callback.
 * The callback must take ownership of freeing the provided jw_dom_node.
 */
PXGRID_STATUS pxgrid_connection_register_topic_notification_handler(pxgrid_connection *connection, pxgrid_notification_cb callback, void *user_data);

/**
 * Make a notification
 *
 * @param connection The connection structure
 * @param capability The capability to notify
 * @param notf The XML payload for the notification
 * @return ::PXGRID_STATUS
 */
PXGRID_STATUS pxgrid_connection_notify(pxgrid_connection *connection, pxgrid_capability *capability, jw_dom_node *notf);

/**
 * Register a handler for query
 *
 * @param connection The connection structure
 * @param ns Namespace of the query to handle
 * @param name Element name of the query to handle
 * @param callback Function to callback when a query is received
 * @param user_data User defined data to be passed to callback
 * @return ::PXGRID_STATUS
 */
PXGRID_STATUS pxgrid_connection_register_query_handler(pxgrid_connection *connection, const char *ns, const char *name, pxgrid_query_cb callback, void *user_data);

/**
 * Set a callback for disconnect event.
 * The callback will be triggered if the pxGrid connection is disconnected for any reason.
 *
 * @param connection The connection structure
 * @param callback Function to callback during disconnect
 */
PXGRID_STATUS pxgrid_connection_set_disconnect_cb(pxgrid_connection *const connection, pxgrid_connection_disconnect_cb disconnect_cb);

/**
 * Set a callback for connected event.
 * The callback will be triggered if the pxGrid connection is connected.
 *
 * @param connection The connection structure
 * @param callback Function to callback after connect
 */
PXGRID_STATUS pxgrid_connection_set_connect_cb(pxgrid_connection * const connection, pxgrid_connection_connect_cb connected_cb);

/**
 * Set the user_data for disconnect event.
 *
 * @param connection The connection structure
 * @param user_data User defined data to be passed to callback
 */
PXGRID_STATUS pxgrid_connection_set_disconnect_cb_user_data(pxgrid_connection *const connection, void *user_data);

/**
 * Set the user_data for disconnect event.
 *
 * @param connection The connection structure
 * @param user_data User defined data to be passed to callback
 */
PXGRID_STATUS pxgrid_connection_set_connect_cb_user_data(pxgrid_connection *const connection, void *user_data);
    
/**
 * Set a callback for account event.
 * The callback will be triggered if the pxGrid connection has account update
 *
 * @param connection The connection structure
 * @param callback Function to callback after connect
 */
PXGRID_STATUS pxgrid_connection_set_account_cb(pxgrid_connection * const connection, pxgrid_connection_account_cb account_cb);

/**
 * Set the user_data for account event.
 *
 * @param connection The connection structure
 * @param user_data User defined data to be passed to callback
 */
PXGRID_STATUS pxgrid_connection_set_account_cb_user_data(pxgrid_connection *const connection, void *user_data);

/**
 * Set callback to configure SSL context manually.
 * This will be called before the SSL connection establish.
 *
 * @param connection The connection structure
 * @param ssl_ctx_cb The callback for setting SSL context
 */
PXGRID_STATUS pxgrid_connection_set_ssl_ctx_cb(pxgrid_connection *connection, pxgrid_connection_ssl_ctx_cb ssl_ctx_cb);

/**
 * Set the user_data that will be passed with the SSL context callback
 *
 * @param connection The connection structure
 * @param user_data Pointer to user data
 */
PXGRID_STATUS pxgrid_connection_set_ssl_ctx_cb_user_data(pxgrid_connection *connection, void *user_data);

    
/**
 * Check if the user assigned to a particular group has permission to query or act upon
 * a particular operation on a particular capability from the Grid Controller
 *
 * @param connection The connection structure
 * @param capability_name The capability name
 * @param operation_name The operation name
 * @param user_name The user name
 * @return true if connected, otherwise false
 */
bool pxgrid_connection_is_authorized(pxgrid_connection *connection, const char* capability_name, const char* operation_name, const char* user);
    

/**
 * Create a reconnection structure for pxGrid connection
 * Reconnection is to automatically check if pxGrid connection requires to be reconnected
 *
 * @param reconnection The pointer to where the newly created reconnection structure will be placed
 * @param connection The connection structure
 * @return ::PXGRID_STATUS
 */
PXGRID_STATUS pxgrid_reconnection_create(pxgrid_reconnection **reconnection, pxgrid_connection *connection);

/**
 * Destroy a reconnection structure
 *
 * @param reconnection The reconnection structure
 * @return ::PXGRID_STATUS
 */
PXGRID_STATUS pxgrid_reconnection_destroy(pxgrid_reconnection *reconnection);

/**
 * Start the reconnection logic
 *
 * @param reconnection The reconnection structure
 * @return ::PXGRID_STATUS
 */
PXGRID_STATUS pxgrid_reconnection_start(pxgrid_reconnection *reconnection);

/**
 * Stop the reconnection logic
 *
 * @param reconnection The reconnection structure
 * @return ::PXGRID_STATUS
 */
PXGRID_STATUS pxgrid_reconnection_stop(pxgrid_reconnection *reconnection);

/**
 * Create a config structure
 *
 * @param config The pointer to where the newly created config structure will be placed
 * @return ::PXGRID_STATUS
 */
PXGRID_STATUS pxgrid_config_create(pxgrid_config **config);

/**
 * Destroy the config structure
 *
 * @param config The config structure
 */
void pxgrid_config_destroy(pxgrid_config *config);

/**
 * Set the hostname of pxGrid controller
 *
 * @param config The config structure
 * @param host The hostname of pxGrid controller
 */
PXGRID_STATUS pxgrid_config_set_host(pxgrid_config * const config, const char *host);

/**
 * Set multiple hostnames of pxGrid controllers
 * There can be more than on pxGrid controllers when using HA mode.
 * This allows multiple hostnames to be specified
 * so that every ::pxgrid_connection_connect will rotate to the next host.
 *
 * @param config The config structure
 * @param hosts The array of hostnames
 * @param hosts_count The number of hostnames
 */
PXGRID_STATUS pxgrid_config_set_hosts(pxgrid_config *const config, const char *hosts[], const int hosts_count);

/**
 * Set multiple groupnames for pxGrid connection
 * There can be more than one group association when using dynamic topics
 * This allows multiple groupnames to be specified
 *
 * @param config The config structure
 * @param groups The array of groupnames
 * @param groups_count The number of groupnames
 */
PXGRID_STATUS pxgrid_config_set_groups(pxgrid_config *const config, const char *groups[], const int groups_count);

/**
 * Set the user name for pxGrid connection
 *
 * @param config The config structure
 * @param user_name User name for the connection
 */
PXGRID_STATUS pxgrid_config_set_user_name(pxgrid_config *const config, const char *username);

/**
 * Set the description for pxGrid connection
 *
 * @param config The config structure
 * @param description Description for the connection
 */
PXGRID_STATUS pxgrid_config_set_description(pxgrid_config * const config, const char *description);

/**
* Set the user group for pxGrid connection
* @param config The config structure
* @param user_group user_group name  for the connection
*/
PXGRID_STATUS pxgrid_config_set_user_group(pxgrid_config * const config, const char *user_group);



/**
 * Set client certificate filename in PEM format
 *
 * @param config The config structure
 * @param filename Pathname to the certificate in the file system
 */
PXGRID_STATUS pxgrid_config_set_client_cert_chain_filename(pxgrid_config *const config, const char *filename);

/**
 * Set client private key filename in PEM format
 *
 * @param config The config structure
 * @param filename Pathname to the private key in the file system
 */
PXGRID_STATUS pxgrid_config_set_client_cert_key_filename(pxgrid_config *const config,  const char *filename);
    
/**
 * Set password to decrypt private key
 *
 * @param config The config structure
 * @param password Password
 */
PXGRID_STATUS pxgrid_config_set_client_cert_key_password(pxgrid_config *const config, const  char *password);

/**
 * Set server certificate filename in PEM format
 *
 * @param config The config structure
 * @param filename Pathname to the certificate in the file system
 */
PXGRID_STATUS pxgrid_config_set_server_cert_chain_filename(pxgrid_config *const config, const char *filename);

/**
 * Set bulk server certificate filename in PEM format
 *
 * @param config The config structure
 * @param filename Pathname to the certificate in the file system
 */
PXGRID_STATUS pxgrid_config_set_bulk_server_cert_chain_filename(pxgrid_config *const config, const char *filename);


/**
 * Set timeout value for sending messages
 *
 * @param config The config structure
 * @param seconds The timeout value in seconds
 */
PXGRID_STATUS pxgrid_config_set_send_timeout_seconds(pxgrid_config *const config, const int seconds);

/**
 * Create a capability structure
 *
 * @param capability The pointer to where the newly created capability structure will be placed
 * @return ::PXGRID_STATUS
 */
PXGRID_STATUS pxgrid_capability_create(pxgrid_capability **capability);

/**
 * Destroy the capability structure
 *
 * @param capability The capability structure
 * @return ::PXGRID_STATUS
 */
PXGRID_STATUS pxgrid_capability_destroy(pxgrid_capability *capability);

/**
 * Set the name for this capability
 *
 * @param capability The capability structure
 * @param name Name of the capability
 * @return ::PXGRID_STATUS
 */
PXGRID_STATUS pxgrid_capability_set_name(pxgrid_capability *capability,const  char *name);

/**
 * Set the name for this dynamic capability
 *
 * @param capability The capability structure
 * @param name Name of the capability
 * @return ::PXGRID_STATUS
 */
PXGRID_STATUS pxgrid_dynamic_capability_set_name(pxgrid_capability *capability,const  char *name);

/**
 * Set the namespace for this capability
 *
 * @param capability The capability structure
 * @param ns Namespace of the capability
 * @return ::PXGRID_STATUS
 */
PXGRID_STATUS pxgrid_capability_set_namespace(pxgrid_capability *capability, const char *ns);

/**
 * Set the filter for this capability.
 * Filter is in XML described by jw_dom structure
 *
 * @param capability The capability structure
 * @param filter The filter in XML
 * @return ::PXGRID_STATUS
 */
PXGRID_STATUS pxgrid_capability_set_filter(pxgrid_capability *capability, jw_dom_node *filter);

/**
 * Subscribe to this capability
 *
 * @param capability The capability structure
 * @param connection The connection structure
 * @return ::PXGRID_STATUS
 */
PXGRID_STATUS pxgrid_capability_subscribe(pxgrid_capability *capability, pxgrid_connection *connection);

/**
 * Subscribe to this dynamic capability
 *
 * @param capability The capability structure
 * @param connection The connection structure
 * @return ::PXGRID_STATUS
 */
PXGRID_STATUS pxgrid_dynamic_capability_subscribe(pxgrid_capability *capability, pxgrid_connection *connection);

/**
 * Register as publisher to this capability
 *
 * @param capability The capability structure
 * @param connection The connection structure
 * @return ::PXGRID_STATUS
 */
PXGRID_STATUS pxgrid_capability_publish(pxgrid_capability *capability, pxgrid_connection *connection);

/**
 * Register as publisher to this dynamic capability
 *
 * @param capability The capability structure
 * @param connection The connection structure
 * @return ::PXGRID_STATUS
 */
PXGRID_STATUS pxgrid_dynamic_capability_publish(pxgrid_capability *capability, pxgrid_connection *connection);

/**
 * Refresh publisher jids for a dynamic capability
 *
 * @param capability The capability structure
 * @param connection The connection structure
 * @return ::void
 */
PXGRID_STATUS pxgrid_dynamic_capability_refresh_publisher_jids(pxgrid_capability *capability, pxgrid_connection *connection);

/**
 * Propose a new capability
 *
 * @param capability The capability structure
 * @param connection The connection structure
 * @param name The capability name
 * @param version The capability version
 * @param querylist The capability querylist
 * @param num_queries Number of capability queries
 * @param actionlist The capability actionlist
 * @param num_actions Number of capability actions
 * @description The capability description
 * @platform The capability vendor platform
 * @return ::PXGRID_STATUS
 */
PXGRID_STATUS pxgrid_capability_propose(pxgrid_capability * capability, pxgrid_connection *connection, 
					const char *name, const char *version, 
					const char **querylist, const int num_queries, 
					const char **actionlist, const int num_actions,
                                        const char *description, const char *vendor_platform); 

/**
 * Modify a capability
 *
 * @param capability The capability structure
 * @param connection The connection structure
 * @param name The capability name
 * @param version The capability version
 * @param querylist The capability querylist
 * @param num_queries Number of capability queries
 * @param actionlist The capability actionlist
 * @param num_actions Number of capability actions
 * @description The capability description
 * @platform The capability vendor platform
 * @return ::PXGRID_STATUS
 */
PXGRID_STATUS pxgrid_capability_modify(pxgrid_capability * capability, pxgrid_connection *connection, 
					const char *name, const char *version, 
					const char **querylist, const int num_queries, 
					const char **actionlist, const int num_actions,
                                        const char *description, const char *vendor_platform); 


typedef struct _pxgrid_bulkdownload pxgrid_bulkdownload;
typedef struct _pxgrid_bulkdownload_iter pxgrid_bulkdownload_iter;
typedef void (*pxgrid_bulkdownload_ssl_ctx_cb)(pxgrid_bulkdownload * bulkdownload, void *ssl_ctx, void *user_data);

/**
 * Create a bulkdownload structure
 *
 * @param bulkdownload The pointer to where the newly created bulkdownload structure will be placed
 * @return ::PXGRID_STATUS
 */
PXGRID_STATUS pxgrid_bulkdownload_create(pxgrid_bulkdownload **bulkdownload, pxgrid_config *config);

/**
 * Destroy the bulkdownload structure
 *
 * @param bulkdownload The bulkdownload structure
 * @return ::PXGRID_STATUS
 */
PXGRID_STATUS pxgrid_bulkdownload_destroy(pxgrid_bulkdownload **bulkdownload);

/**
 * Set the request XML
 *
 * @param bulkdownload The bulkdownload structure
 * @param request The request in XML format
 * @return ::PXGRID_STATUS
 */
PXGRID_STATUS pxgrid_bulkdownload_set_request(pxgrid_bulkdownload * bulkdownload, jw_dom_node *request);

/**
 * Set the URL for the bulk download
 *
 * @param bulkdownload The bulkdownload structure
 * @param url The URL for bulk download
 * @return ::PXGRID_STATUS
 */
PXGRID_STATUS pxgrid_bulkdownload_set_url(pxgrid_bulkdownload * bulkdownload, const char *url);

/**
 * Open the bulk download operation
 *
 * @param bulkdownload The bulkdownload structure
 * @return ::PXGRID_STATUS
 */
PXGRID_STATUS pxgrid_bulkdownload_open(pxgrid_bulkdownload *bulkdownload);

/**
 * Get the next item
 *
 * @param bulkdownload The bulkdownload structure
 * @param item The pointer to where the next item will be placed
 * @return ::PXGRID_STATUS
 *
 * If pxgrid_bulkdownload_next() returns a valid (not null) item object,
 * the caller function must take ownership of freeing the OUT jw_dom_node. 	
 */

PXGRID_STATUS pxgrid_bulkdownload_next(pxgrid_bulkdownload * bulkdownload, jw_dom_node **item);

/**
 * Close the bulk download operation
 *
 * @param bulkdownload The bulkdownload structure
 * @return ::PXGRID_STATUS
 */
PXGRID_STATUS pxgrid_bulkdownload_close(pxgrid_bulkdownload *bulkdownload);

/**
 * Bulk download open result callback
 * pxgrid API user to register a callback before performing bulk download operation
 * @param bulkdownload The bulkdownload structure
 * @param status PXGRID_STATUS
 * @error_str error string pertaining to status. It's owned by pxgrid library and will be freed after this call. API user to duplicate it for there use.
 * @curl_error_code valid curl error code if status == PXGRID_STATUS_REST_ERROR 0 otherwise.
 * @return ::void
 */
typedef void (*pxgrid_bulkdownload_open_result_cb)(pxgrid_bulkdownload * bulkdownload, void *user_data, PXGRID_STATUS status, const char *error_str, int curl_error_code);

void pxgrid_bulkdownload_set_open_result_cb(pxgrid_bulkdownload * bulkdownload, pxgrid_bulkdownload_open_result_cb cb);

void pxgrid_bulkdownload_set_open_result_cb_user_data(pxgrid_bulkdownload *bulkdownload, void *user_data);
/**
 * Set callback to configure SSL context manually.
 * This will be called before the SSL connection establish.
 *
 * @param bulkdownload The bulkdownload structure
 * @param cb The callback for setting SSL context
 */
void pxgrid_bulkdownload_set_ssl_ctx_cb(pxgrid_bulkdownload * bulkdownload, pxgrid_bulkdownload_ssl_ctx_cb cb);

/**
 * Set the user_data that will be passed with the SSL context callback
 *
 * @param bulkdownload The bulkdownload structure
 * @param user_data Pointer to user data
 */
void pxgrid_bulkdownload_set_ssl_ctx_cb_user_data(pxgrid_bulkdownload * bulkdownload, void *user_data);

/**
 * Get the text message for PXGRID_STATUS
 *
 * @param status ::PXGRID_STATUS
 * @return Text message corresponding to the status
 */
const char *pxgrid_status_get_message(PXGRID_STATUS status);

/**
 * Get the text message  for bulkdownload 
 * @IN param bulkdownload: A pointer of pxgrid_bulkdownload structure 
  * @OUT description :param buffer pointer (discovery mode must be NULL)
 * @INdescription_length: buffer size , Length of buffer.
 * @return status ::PXGRID_STATUS
 */
PXGRID_STATUS pxgrid_bulkdownload_get_error_details(pxgrid_bulkdownload * bulkdownload,char * description,int description_length);

/**
 * Set the log callback function that will be  used to redirect the pxgrid log
 * @param pxgrid_log_cb  client log function
 * status ::PXGRID_STATUS
 */
PXGRID_STATUS pxgrid_log_set_callback(pxgrid_log_cb log_callback);

/**
 * Set the log level that will be  used to redirect the pxgrid log
 * @param PXGRID_LOG_LEVEL  log level
 * status ::PXGRID_STATUS
 */
PXGRID_STATUS pxgrid_log_set_level( PXGRID_LOG_LEVEL loglevel);
/**
 * Find the sender
 */
PXGRID_STATUS pxgrid_xml_get_sender(jw_dom_node *node, char *sender);

    

#ifdef __cplusplus
}
#endif

#endif /* PXGRID_H_ */

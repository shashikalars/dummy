#include <stdlib.h>
#include <unistd.h>

#include "pxgrid.h"
#include <openssl/ssl.h>

#include "anc_policy_crud.h"
#include "anc_endpoint_action.h"
#include "anc_endpoint_read.h"
#include "anc_subscribe.h"

#define UNUSED(x) (void)(x)
#define str(x) #x

PXGRID_STATUS       status          = PXGRID_STATUS_OK;
pxgrid_connection   *connection     = NULL;
pxgrid_config       *conn_config    = NULL;
helper_config       *hconfig        = NULL;
pxgrid_capability   *capability     = NULL;

typedef enum
{
    ANC_ACTION_EXIT = 0,
    ANC_APPLY_ENDPOINT_POLICY_BY_MAC,
    ANC_CLEAR_ENDPOINT_POLICY_BY_MAC,
    ANC_APPLY_ENDPOINT_POLICY_BY_IP,
    ANC_CLEAR_ENDPOINT_POLICY_BY_IP,
    ANC_SUBSCRIBE,
    ANC_CREATE_POLICY,
    ANC_UPDATE_POLICY,
    ANC_DELETE_POLICY,
    ANC_GET_POLICY_BY_NAME,
    ANC_GET_ALL_POLICIES,
    ANC_GET_ENDPOINT_BY_MAC,
    ANC_GET_ENDPOINT_BY_IP,
    ANC_GET_ALL_ENDPOINTS,
    ANC_GET_ENDPOINT_BY_POLICY,
    ANC_ACTION_MAX
} anc_operand;

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

static void _xgrid_connect(int argc, char **argv) {

    helper_config_create(&hconfig, argc, argv);
    if(!hconfig) 
    {
        printf("Unable to create hconfig object\n");
        exit(EXIT_FAILURE); 
    } 
    helper_pxgrid_config_create(hconfig , &conn_config);
    pxgrid_config_set_user_group(conn_config, "ANC");
    //Set grid timeout to be greater than ANC operation timeout
    pxgrid_config_set_send_timeout_seconds(conn_config, 75);
    pxgrid_connection_create( &connection );
     
    // Set connection configuration data
    pxgrid_connection_set_config(connection , conn_config);

    // Set Call back
    pxgrid_connection_set_disconnect_cb(connection, _on_disconnected);  
    pxgrid_connection_set_connect_cb(connection, _on_connected);
    
    pxgrid_connection_set_ssl_ctx_cb(connection, (pxgrid_connection_ssl_ctx_cb)_user_ssl_ctx_cb);
    pxgrid_connection_set_ssl_ctx_cb_user_data(connection, (helper_config *)hconfig);

    pxgrid_capability_create(&capability);

    char namespacebuf[] = "http://www.cisco.com/pxgrid/anc";
    char namebuf[] = "AdaptiveNetworkControlCapability";
    
    pxgrid_capability_set_namespace(capability, namespacebuf);
    pxgrid_capability_set_name(capability, namebuf);
      
    pxgrid_connection_connect(connection);
}

static void _xgrid_disconnect() {
    if (connection && pxgrid_connection_is_connected(connection)) {
        pxgrid_connection_disconnect(connection);
        printf("*** disconnected\n");
    }

    if (connection) pxgrid_connection_destroy(connection);
    if (conn_config) pxgrid_config_destroy(conn_config);
    if (hconfig) helper_config_destroy(hconfig);
    if (capability) pxgrid_capability_destroy(capability);
}

int main(int argc, char **argv)
{
    _xgrid_connect(argc, argv);

    pxgrid_capability_subscribe(capability, connection);

    char            anc_num_str[16]         = {0};
    char            anc_num_extra_str[16]   = {0};
    unsigned int    anc_num                 = ANC_ACTION_EXIT;

    char            policy_name_str[66]         = {0};
    char            policy_name[66]             = {0};
    char            policy_name_extra_str[66]   = {0};

    char            mac_address_str[24]         = {0};
    char            mac_address[24]             = {0};
    char            mac_address_extra_str[24]   = {0};

    char            ip_address_str[48]          = {0};
    char            ip_address[48]              = {0};
    char            ip_address_extra_str[48]    = {0};
    int             actions_chosen[NUM_ANC_ACTIONS];
    memset(actions_chosen, 0, NUM_ANC_ACTIONS*sizeof(int));

    do {
        anc_num = ANC_ACTION_EXIT;

        printf ("Choose ANC Action:\n");
        printf ("0. Exit\n");
        printf ("1. ApplyEndpointPolicyByMAC\n");
        printf ("2. ClearEndpointPolicyByMAC\n");
        printf ("3. ApplyEndpointPolicyByIP\n");
        printf ("4. ClearEndpointPolicyByIP\n");
        printf ("5. Subscribe\n");
        printf ("6. CreatePolicy\n");
        printf ("7. UpdatePolicy\n");
        printf ("8. DeletePolicy\n");
        printf ("9. GetPolicyByName\n");
        printf ("10. GetAllPolicies\n");
        printf ("11. GetEndPointByMAC\n");
        printf ("12. GetEndpointByIP\n");
        printf ("13. GetAllEndpoints\n");
        printf ("14. GetEndpointByPolicy\n");
        printf ("Enter action #:");

        fgets(anc_num_str, sizeof(anc_num_str), stdin);
        sscanf(anc_num_str, "%i%[^\n]", &anc_num, anc_num_extra_str);

        switch (anc_num) {
            case ANC_APPLY_ENDPOINT_POLICY_BY_MAC:
                printf("Policy name: ");
                fgets(policy_name_str, sizeof(policy_name_str), stdin);
                sscanf(policy_name_str, "%s%[^\n]", policy_name, policy_name_extra_str);

                printf("MAC Address: ");
                fgets(mac_address_str, sizeof(mac_address_str), stdin);
                sscanf(mac_address_str, "%s%[^\n]", mac_address, mac_address_extra_str);

                anc_apply_endpoint_policy_by_mac_request(connection, capability, policy_name, mac_address);
                break;
            case ANC_CLEAR_ENDPOINT_POLICY_BY_MAC:
                printf("MAC Address: ");
                fgets(mac_address_str, sizeof(mac_address_str), stdin);
                sscanf(mac_address_str, "%s%[^\n]", mac_address, mac_address_extra_str);

                anc_clear_endpoint_policy_by_mac_request(connection, capability, mac_address);
                break;
            case ANC_APPLY_ENDPOINT_POLICY_BY_IP:
                printf("Policy name: ");
                fgets(policy_name_str, sizeof(policy_name_str), stdin);
                sscanf(policy_name_str, "%s%[^\n]", policy_name, policy_name_extra_str);

                printf("IP Address: ");
                fgets(ip_address_str, sizeof(ip_address_str), stdin);
                sscanf(ip_address_str, "%s%[^\n]", ip_address, ip_address_extra_str);

                anc_apply_endpoint_policy_by_ip_request(connection, capability, policy_name, ip_address);
                break;
            case ANC_CLEAR_ENDPOINT_POLICY_BY_IP:
                printf("IP Address: ");
                fgets(ip_address_str, sizeof(ip_address_str), stdin);
                sscanf(ip_address_str, "%s%[^\n]", ip_address, ip_address_extra_str);

                anc_clear_endpoint_policy_by_ip_request(connection, capability, ip_address);
                break;
            case ANC_SUBSCRIBE:
                subscribe(connection);
                printf("Hit Enter to disconnect: ");
                char c=getchar();
                anc_num = ANC_ACTION_EXIT;
                break;
            case ANC_CREATE_POLICY:
                printf("Policy name: ");
                fgets(policy_name_str, sizeof(policy_name_str), stdin);
                sscanf(policy_name_str, "%s%[^\n]", policy_name, policy_name_extra_str);
                anc_action_prompt(actions_chosen);

                anc_createPolicyRequest(connection, capability, policy_name, actions_chosen);

                break;
            case ANC_UPDATE_POLICY:
                printf("Policy name: ");
                fgets(policy_name_str, sizeof(policy_name_str), stdin);
                sscanf(policy_name_str, "%s%[^\n]", policy_name, policy_name_extra_str);
                anc_action_prompt(actions_chosen);

                anc_updatePolicyRequest(connection, capability, policy_name, actions_chosen);
                break;
            case ANC_DELETE_POLICY:
                printf("Policy name: ");
                fgets(policy_name_str, sizeof(policy_name_str), stdin);
                sscanf(policy_name_str, "%s%[^\n]", policy_name, policy_name_extra_str);

                anc_deletePolicyRequest(connection, capability, policy_name);
                break;
            case ANC_GET_POLICY_BY_NAME:
                printf("Policy name: ");
                fgets(policy_name_str, sizeof(policy_name_str), stdin);
                sscanf(policy_name_str, "%s%[^\n]", policy_name, policy_name_extra_str);

                anc_getPolicyByName(connection, capability, policy_name);
                break;
            case ANC_GET_ALL_POLICIES:
                anc_getAllPolicies(connection, capability);
                break;
            case ANC_GET_ENDPOINT_BY_MAC:
                printf("MAC Address: ");
                fgets(mac_address_str, sizeof(mac_address_str), stdin);
                sscanf(mac_address_str, "%s%[^\n]", mac_address, mac_address_extra_str);

                anc_getEndpointByMACRequest(connection, capability, mac_address);
                break;
            case ANC_GET_ENDPOINT_BY_IP:
                printf("IP Address: ");
                fgets(ip_address_str, sizeof(ip_address_str), stdin);
                sscanf(ip_address_str, "%s%[^\n]", ip_address, ip_address_extra_str);

                anc_getEndpointByIPRequest(connection, capability, ip_address);
                break;
            case ANC_GET_ALL_ENDPOINTS:
                anc_getAllEndpointsRequest(connection, capability);
                break;
            case ANC_GET_ENDPOINT_BY_POLICY:
                printf("Policy name: ");
                fgets(policy_name_str, sizeof(policy_name_str), stdin);
                sscanf(policy_name_str, "%s%[^\n]", policy_name, policy_name_extra_str);

                anc_getEndpointByPolicyRequest(connection, capability, policy_name);
            default:
                printf("!!!!!!!! IMPLEMENTED\n");
                break;
        }

        memset(anc_num_str, 0, sizeof(anc_num_str));
        memset(anc_num_extra_str, 0, sizeof(anc_num_extra_str));

        memset(policy_name_str, 0, sizeof(policy_name_str));
        memset(policy_name, 0, sizeof(policy_name));
        memset(policy_name_extra_str, 0, sizeof(policy_name_extra_str));

        memset(mac_address_str, 0, sizeof(mac_address_str));
        memset(mac_address, 0, sizeof(mac_address));
        memset(mac_address_extra_str, 0, sizeof(mac_address_extra_str));

        memset(ip_address_str, 0, sizeof(ip_address_str));
        memset(ip_address, 0, sizeof(ip_address));
        memset(ip_address_extra_str, 0, sizeof(ip_address_extra_str));

        memset(actions_chosen, 0, NUM_ANC_ACTIONS*sizeof(int));
        

    } while(anc_num != ANC_ACTION_EXIT);

    _xgrid_disconnect();
    return 0;
}

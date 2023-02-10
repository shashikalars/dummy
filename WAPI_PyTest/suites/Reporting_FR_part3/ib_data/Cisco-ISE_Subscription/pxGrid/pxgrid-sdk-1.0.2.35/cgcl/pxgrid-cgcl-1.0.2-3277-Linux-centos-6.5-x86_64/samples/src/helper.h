/*
 * helper.h
 */

#include "pxgrid.h"
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <stdbool.h>
#include <unistd.h>
#include <jabberwerx/jabberwerx.h>
#include <openssl/ssl.h>
#define IDGROUP_MAX 256
#define UNUSED(x) (void)(x)
static const int SUCCESS = 1;
static const int FAILURE = 0;

// Flatten structures for easier access
typedef struct {
    const char *id;
    const char *user_name;
    const char *state;
    const char *ip;
    const char *mac;
    const char *anc_status;
} ise_session;

typedef struct {
    const char *uesr_name;
    int group_size;
    const char *group_names[IDGROUP_MAX];
} ise_identity_group;

typedef struct {
    const char *id;
    const char *name;
    const char *fqname;
} ise_endpoint_profile;

typedef struct {
    const char *id;
    const char *name;
    const char *description;
    const char *tag;
} ise_security_group;


typedef struct {
    char *user_name;
	char *description;
	char *host;
    char *client_cert_chain_filename;
    char *client_cert_key_filename;
    char *client_cert_key_password;
    char *server_cert_chain_filename;
    char *bulk_server_cert_chain_filename;
    char *rest_host;
	char *filter;
    char *cap_name;
    char *cap_version;
    char *cap_query;
    char *cap_action;
    char *cap_description;
    char *cap_vendorplatform;
    char *group;
	bool is_reconnection_mode;
} helper_config;

typedef struct {
    helper_config *hconfig;
    pxgrid_config *conn_config;
    pxgrid_connection *connection;
} helper_connection;

//sxp bindings structure

typedef struct {
	const char *ipPrefix;
	const char *tag;
	const char *source;
	const char *peerSeq;	
} ise_sxpbinding;

//ANC policy action user choice
typedef enum {
    END_POLICY_ACTION = 0,
    QUARANTINE,
    REMEDIATE,
    PROVISIONING,
    SHUT_DOWN,
    PORT_BOUNCE
} anc_action;

//ANC policy action name 
static char *POLICY_ACTION_STRING[] = {
    "EndPolicyAction", "Quarantine", "Remediate", "Provisioning", "ShutDown", "PortBounce"
};

static const int NUM_ANC_ACTIONS = 5;

void ise_session_create(ise_session **_session, jw_dom_node *session_node);
void ise_session_destroy(ise_session *session);
void ise_session_print(ise_session *session);
void ise_identity_group_create(ise_identity_group **_idgroup, jw_dom_node *user_node);
void ise_identity_group_destroy(ise_identity_group *idgroup);
void ise_identity_group_print(ise_identity_group *idgroup);
void ise_endpoint_profile_create(ise_endpoint_profile **_profile, jw_dom_node *profile_node);
void ise_endpoint_profile_destroy(ise_endpoint_profile *profile);
void ise_endpoint_profile_print(ise_endpoint_profile *profile);
void ise_security_group_create(ise_security_group **_group, jw_dom_node *group_node);
void ise_security_group_destroy(ise_security_group *group);
void ise_security_group_print(ise_security_group *group);
void ise_print_changetype(jw_dom_node *node);

void helper_print_error(PXGRID_STATUS status);
void helper_print_jw_dom(jw_dom_node *node);
bool helper_jw_dom_add_child_with_text(jw_dom_node *parent, const char *child_name, const char *text, jw_err *err);


int helper_config_create(helper_config **hconfig, int argc, char *argv[]);
int helper_pxgrid_config_create(const helper_config *const hconfig, pxgrid_config **_config);
void helper_config_destroy(helper_config *hconfig);
void helper_pxgrid_bulkdownload_open_result_cb(pxgrid_bulkdownload * bulkdownload,  void *user_data, PXGRID_STATUS status, const char *error_str, int curl_error_code);

void helper_connection_create(helper_connection **helper, int argc, char *argv[]);
void helper_connection_connect(helper_connection *helper);
void helper_connection_disconnect(helper_connection *helper);
void helper_connection_destroy(helper_connection *helper);
pxgrid_connection *helper_connection_get_pxgrid_connection(helper_connection *helper);

bool helper_prompt(const char *message, char *result);

//SXP Bindings function
void ise_sxpbinding_create(ise_sxpbinding **_sxpbindings, jw_dom_node *sxpbindings_node);
void ise_sxpbinding_destroy(ise_sxpbinding *sxpbinding);
void ise_sxpbinding_print(ise_sxpbinding *sxpbinding);

void anc_action_prompt(int *actions_chosen);

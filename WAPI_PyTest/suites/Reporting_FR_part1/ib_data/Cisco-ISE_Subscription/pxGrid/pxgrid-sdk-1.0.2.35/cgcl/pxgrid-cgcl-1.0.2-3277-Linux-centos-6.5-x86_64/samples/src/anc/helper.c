/*
 * helper.c
 */

#include "pxgrid.h"
#include "helper.h"
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <stdbool.h>
#include <unistd.h>
#include <jabberwerx/jabberwerx.h>
#include <openssl/ssl.h>

#define UNUSED(x) (void)(x)

// SXP binding helper functions
void ise_sxpbinding_create(ise_sxpbinding **_sxpbindings, jw_dom_node *sxpbindings_node) {
	
	// Create and Allocate  buffer to ise_sxpbindings
	ise_sxpbinding *sxpbinding = malloc(sizeof(ise_sxpbinding));
	
	//Get ipPrefix element
	jw_dom_node *ipPrefix_node = jw_dom_get_first_element(sxpbindings_node, "ipPrefix");
	if (ipPrefix_node) {
		sxpbinding->ipPrefix = jw_dom_get_first_text(ipPrefix_node);
	}

	//Get tag element
	jw_dom_node *tag_node = jw_dom_get_first_element(sxpbindings_node, "tag");
	if (tag_node) {
		sxpbinding->tag = jw_dom_get_first_text(tag_node);
	}

	//Get source element
	jw_dom_node *source_node = jw_dom_get_first_element(sxpbindings_node, "source");
	if (source_node) {
		sxpbinding->source = jw_dom_get_first_text(source_node);
	}

	//Get peerSeq element
	jw_dom_node *peerSeq_node = jw_dom_get_first_element(sxpbindings_node, "peerSequence");
	if (peerSeq_node) {
		sxpbinding->peerSeq = jw_dom_get_first_text(peerSeq_node);
	}
		
	*_sxpbindings = sxpbinding;
}

void ise_sxpbinding_destroy(ise_sxpbinding *sxpbinding) {
	free(sxpbinding);
}


void ise_sxpbinding_print(ise_sxpbinding *sxpbinding) {
	printf("ipPrefix=%s ", sxpbinding->ipPrefix);
	printf("tag=%s ", sxpbinding->tag);
	printf("source=%s ", sxpbinding->source);
	printf("peerSeq=%s ", sxpbinding->peerSeq);

	printf("\n");
}



void ise_session_create(ise_session **_session, jw_dom_node *session_node) {
    ise_session *session = malloc(sizeof(ise_session));
	jw_dom_node *gid_node = jw_dom_get_first_element(session_node, "gid");
    if (gid_node) {
        session->id = jw_dom_get_first_text(gid_node);
    }
    
    jw_dom_node *state_node = jw_dom_get_first_element(session_node, "state");
    if (state_node) {
        session->state = jw_dom_get_first_text(state_node);
    }
    
	jw_dom_node *user_node = jw_dom_get_first_element(session_node, "user");
    if (user_node) {
        jw_dom_node *name_node = jw_dom_get_first_element(user_node, "name");
        if (name_node) {
            session->user_name = jw_dom_get_first_text(name_node);
        }
    }

    jw_dom_node *intf_node = jw_dom_get_first_element(session_node, "interface");
    char buffer[4096];
    memset(buffer, 0, sizeof(buffer));
    char *tmp = NULL;
    if (intf_node) {
        jw_dom_node *ip_intf_node = jw_dom_get_first_element(intf_node, "ipIntfID");
        while (ip_intf_node) {
            jw_dom_node *ip_node = jw_dom_get_first_element(ip_intf_node, "ipAddress");
            if (ip_node) {
                tmp = jw_dom_get_first_text(ip_node);
                strncat(buffer, tmp, strlen(tmp));
                strncat(buffer, ",", sizeof(char));
            }
            ip_intf_node = jw_dom_get_sibling(ip_intf_node);
        }
        if(strlen(buffer) > 0) {
            buffer[strlen(buffer)-1] = '\0';
            session->ip = strdup(buffer);
        }

        jw_dom_node *mac_node = jw_dom_get_first_element(intf_node, "macAddress");
        if (mac_node) {
            session->mac = jw_dom_get_first_text(mac_node);
        }
    }

    jw_dom_node *anc_status = jw_dom_get_first_element(session_node, "ANCStatus");
	if (anc_status) {
	    session->anc_status = jw_dom_get_first_text(anc_status);
	}
	else {
	    session->anc_status = NULL;
	}
    
    *_session = session;
}

void ise_session_destroy(ise_session *session) {
    free(session);
}


void ise_session_print(ise_session *session) {
    printf("session=%s ", session->id);
    printf("state=%s ", session->state);
    printf("user=%s ", session->user_name);
    printf("ip=%s ", session->ip);
    printf("mac=%s ", session->mac);
    printf("anc_status=%s ", session->anc_status);
    printf("\n");
}

void ise_identity_group_create(ise_identity_group **_idgroup, jw_dom_node *user_node) {
    ise_identity_group *idgroup = malloc(sizeof(ise_identity_group));
    jw_dom_node *name_node = jw_dom_get_first_element(user_node, "name");
    if (name_node) {
        idgroup->uesr_name = jw_dom_get_first_text(name_node);
    }
    idgroup->group_size = 0;
    jw_dom_node *list_node = jw_dom_get_first_element(user_node, "groupList");
    if (list_node) {
        jw_dom_node *obj_node = jw_dom_get_first_child(list_node);
        while (obj_node && idgroup->group_size < IDGROUP_MAX) {
            name_node = jw_dom_get_first_element(obj_node, "name");
            if (name_node) {
                idgroup->group_names[idgroup->group_size] = jw_dom_get_first_text(name_node);
                idgroup->group_size++;
            }
            obj_node = jw_dom_get_sibling(obj_node);
        }
    }
    *_idgroup = idgroup;
}

void ise_identity_group_destroy(ise_identity_group *idgroup) {
    free(idgroup);
}

void ise_identity_group_print(ise_identity_group *idgroup) {
    int i;
    printf("user=%s ", idgroup->uesr_name);
    printf("group=");
    for (i = 0; i < idgroup->group_size; i++) {
        printf("%s ", idgroup->group_names[i]);
    }
    printf("\n");
}

void ise_endpoint_profile_create(ise_endpoint_profile **_profile, jw_dom_node *profile_node) {
    ise_endpoint_profile *profile = malloc(sizeof(ise_endpoint_profile));
    jw_dom_node *id_node = jw_dom_get_first_element(profile_node, "id");
    if (id_node) {
        profile->id = jw_dom_get_first_text(id_node);
    }
    jw_dom_node *name_node = jw_dom_get_first_element(profile_node, "name");
    if (name_node) {
        profile->name = jw_dom_get_first_text(name_node);
    }
    jw_dom_node *fqname_node = jw_dom_get_first_element(profile_node, "fqname");
    if (fqname_node) {
        profile->fqname = jw_dom_get_first_text(fqname_node);
    }
    *_profile = profile;
}

void ise_endpoint_profile_destroy(ise_endpoint_profile *profile) {
    free(profile);
}

void ise_endpoint_profile_print(ise_endpoint_profile *profile) {
    printf("id=%s name=%s fqname=%s\n", profile->id, profile->name, profile->fqname);
}

void ise_security_group_create(ise_security_group **_group, jw_dom_node *group_node) {
    ise_security_group *group = malloc(sizeof(ise_security_group));
    jw_dom_node *id_node = jw_dom_get_first_element(group_node, "id");
    if (id_node) {
        group->id = jw_dom_get_first_text(id_node);
    }
    jw_dom_node *name_node = jw_dom_get_first_element(group_node, "name");
    if (name_node) {
        group->name = jw_dom_get_first_text(name_node);
    }
    jw_dom_node *description_node = jw_dom_get_first_element(group_node, "description");
    if (description_node) {
        group->description = jw_dom_get_first_text(description_node);
    }
    jw_dom_node *tag_node = jw_dom_get_first_element(group_node, "tag");
    if (tag_node) {
        group->tag = jw_dom_get_first_text(tag_node);
    }
    *_group = group;
}

void ise_security_group_destroy(ise_security_group *group) {
    free(group);
}

void ise_security_group_print(ise_security_group *group) {
    printf("id=%s name=%s description=%s tag=%s\n", group->id, group->name, group->description, group->tag);
}





void helper_print_error(PXGRID_STATUS status) {
	printf("Error PXGRID_STATUS=%s\n", pxgrid_status_get_message(status));
}

void helper_print_jw_dom(jw_dom_node *node) {
	jw_err err;
    char *xml;
    size_t len;
    jw_serialize_xml(node, &xml, &len, &err);
    printf("node=%s\n", xml);
}

static void helper_print_program_usage( FILE *stream, char *program_pathname)
{
	char *program_name = NULL;

	program_name = strrchr(program_pathname, '/');
	if(NULL == program_name) {
		program_name = program_pathname;
	}
	else {
		program_name +=1;
	}

	fprintf(stream, "Usage: %s options [ arguments ... ]\n", program_pathname);

	if( strcmp("sessions_download_filtered", program_name)== 0 )
	{
		fprintf(stream, "Usage: %s [-a pxgrid_host] [-u username] [-d description (optional)] [-c cert_filename] [-k cert_key_filename] [-p cert_key_password] [-s server_cert_file] [-b bulk_server_cert_file] [-f IpAddress/NetMask ][-r rest_host]\n", program_pathname);
	}
	else if( strcmp("session_subscriber_filtered", program_name)== 0 )
	{
		fprintf(stream, "Usage: %s [-a pxgrid_host] [-u username] [-d description (optional)] [-c cert_filename] [-k cert_key_filename] [-p cert_key_password] [-s server_cert_file] [-f IpAddress/NetMask ]\n", program_pathname);
	}
	else if(strcmp("sessions_download", program_name)== 0 || strcmp("id_group_download", program_name)== 0)
	{
		fprintf(stream, "Usage: %s [-a pxgrid_host] [-u username] [-d description (optional)] [-c cert_filename] [-k cert_key_filename] [-p cert_key_password] [-s server_cert_file] [-b bulk_server_cert_file] [-r rest_host]\n", program_pathname);	
	}
	else if( strcmp("propose_capability", program_name)== 0 )
	{
		fprintf(stream, "Usage: %s [-a pxgrid_host] [-u username] [-d description (optional)] [-c cert_filename] [-k cert_key_filename] [-p cert_key_password] [-s server_cert_file] [-n capability_name] [-v capability_version] [-q capability_query] [-t capability_action] [-e capability_description] [-o capability_vendor_platform]\n", program_pathname);	
	}
        else if( strcmp("modify_capability", program_name)== 0 )
	{
		fprintf(stream, "Usage: %s [-a pxgrid_host] [-u username] [-d description (optional)] [-c cert_filename] [-k cert_key_filename] [-p cert_key_password] [-s server_cert_file] [-n capability_name] [-v capability_version] [-q capability_query] [-t capability_action] [-e capability_description] [-o capability_vendor_platform]\n", program_pathname);	
	}
        else if( strcmp("multigroupclient", program_name)== 0 )
	{
		fprintf(stream, "Usage: %s [-a pxgrid_host] [-u username] [-d description (optional)] [-c cert_filename] [-k cert_key_filename] [-p cert_key_password] [-s server_cert_file] [-g groups]\n", program_pathname);	
	}
	else {
		fprintf(stream, "Usage: %s [-a pxgrid_host] [-u username] [-d description (optional)] [-c cert_filename] [-k cert_key_filename] [-p cert_key_password] [-s server_cert_file]\n", program_pathname);
	}
}

static bool helper_is_bulk_server_cert_program(char *program_pathname) {
	char *program_name = NULL;
	bool retval = false;

	program_name = strrchr(program_pathname, '/');
	if(NULL == program_name) {
		program_name = program_pathname;
	}
	else {
		program_name +=1;
	}

	if(strcmp("sessions_download_filtered", program_name)== 0) {
		retval = true;
	}
	else if(strcmp("sessions_download", program_name)== 0) {
		retval = true;
	}
	else if(strcmp("id_group_download", program_name)== 0) {
		retval = true;
	}
	else {
		retval = false;
	}
	return retval;
}

int helper_config_create(helper_config **_config, int argc, char *argv[]) 
{
	int retval = FAILURE;
	bool isHost = false;
	bool isUserName = false;
	bool isClientCertChainfilename = false;
	bool isCertKeyfilename = false;
	bool isCertKeyPasswd =  false;
	bool isServerCertChainfilename = false;
	bool isBulkServerCertChainfilename = false;

	helper_config *config = malloc(sizeof(helper_config));
	if(NULL == config)
	{
		printf("*** Memory allocation failed\n");
		return retval;	
	}
    memset(config, 0, sizeof(helper_config));
    int opt;
    config->description = strdup("GCL for C sample");	
	
	config->is_reconnection_mode = false;
	while ((opt = getopt(argc, argv, "a:u:d:c:k:p:s:b:f:r:n:v:q:t:e:o:g:m:")) != -1) 
	{
		switch (opt) 
		{
            case 'a':
                config->host = strdup(optarg);
				isHost = true;
                break;
            case 'u':
                config->user_name = strdup(optarg);
				isUserName = true;
                break;
            case 'd':
                config->description = strdup(optarg);
                break;
            case 'c':
                config->client_cert_chain_filename = strdup(optarg);
				isClientCertChainfilename = true;
                break;
            case 'k':
                config->client_cert_key_filename = strdup(optarg);
				isCertKeyfilename = true;
                break;
            case 'p':
                config->client_cert_key_password = strdup(optarg);
				isCertKeyPasswd = true;
                break;
            case 's':
                config->server_cert_chain_filename = strdup(optarg);
				isServerCertChainfilename = true;
                break;
            case 'b':
                config->bulk_server_cert_chain_filename = strdup(optarg);
				isBulkServerCertChainfilename = true;
                break;
            case 'r':
                config->rest_host = strdup(optarg);
				break;
			case 'f':
                config->filter = strdup(optarg);
				break;
            case 'n':
                config->cap_name = strdup(optarg);
                break;
            case 'v':
                config->cap_version = strdup(optarg);
                break;
            case 'q':
                config->cap_query = strdup(optarg);
                break;
            case 't':
                config->cap_action = strdup(optarg);
                break;
            case 'e':
                config->cap_description = strdup(optarg);
                break;
            case 'o':
                config->cap_vendorplatform = strdup(optarg);
                break;
            case 'g':
                config->group = strdup(optarg);
                break;
   
	default: ;                
        }
    }
    
    // Validations
	
	if( !(isHost && isUserName && isClientCertChainfilename && 
		isCertKeyfilename && isCertKeyPasswd &&	isServerCertChainfilename)  )
	{
		helper_print_program_usage(stderr, argv[0]);
		goto cleanup;
	}
	if( helper_is_bulk_server_cert_program(argv[0]) && !isBulkServerCertChainfilename ) {
		helper_print_program_usage(stderr, argv[0]);
		goto cleanup;
	}
    
    if (config->client_cert_key_filename) {
        if (access(config->client_cert_key_filename, R_OK) != 0) {
            perror("Unable to read client cert key file");
		goto cleanup;
        }
    }
    if (config->client_cert_chain_filename) {
        if (access(config->client_cert_chain_filename, R_OK) != 0) {
            perror("Unable to read client cert chain file");
		goto cleanup;
        }
    }
    if (config->server_cert_chain_filename) {
        if (access(config->server_cert_chain_filename, R_OK) != 0) {
            perror("Unable to read server cert chain file");
		goto cleanup;
        }
    }
    if (config->bulk_server_cert_chain_filename) {
        if (access(config->bulk_server_cert_chain_filename, R_OK) != 0) {
            perror("Unable to read secure server cert chain file");
		goto cleanup;
        }
    }

	*_config = config;
	return SUCCESS;

cleanup:
	free(config);
	*_config = NULL;
	exit(1);
	return retval;	
}

int helper_pxgrid_config_create(const helper_config * const hconfig, pxgrid_config **_config) 
{
	pxgrid_config *config = NULL;
	char *tf = NULL;
		
	if( PXGRID_STATUS_OK != pxgrid_config_create(&config) )
	{
		printf("*** pxgrid_config_create failed\n");
		return FAILURE;	
	}
	char *hostnames[20];
	int nHosts =0 ;
	tf = NULL;
	tf = strtok(hconfig->host ," ");	
	while (tf != NULL)
	{
	    hostnames[nHosts] = (char*) calloc(strlen(tf)+1 , sizeof(char));
		strncpy(hostnames[nHosts] ,tf ,strlen(tf)+1 );	
	    tf = strtok (NULL," ");	 
	    nHosts++;
	}

        char *groupnames[20];
	int nGroups = 0;
	tf = NULL;
	tf = strtok(hconfig->group,",");	
	while (tf != NULL)
	{
	    groupnames[nGroups] = (char*) calloc(strlen(tf)+1 , sizeof(char));
		strncpy(groupnames[nGroups] ,tf ,strlen(tf)+1 );	
	    tf = strtok (NULL,",");	 
	    nGroups++;
	}
	
	pxgrid_config_set_hosts(config, (const char **)hostnames , nHosts);
        pxgrid_config_set_groups(config, (const char **)groupnames , nGroups);
	pxgrid_config_set_user_name(config, hconfig->user_name);
	pxgrid_config_set_description(config, hconfig->description);
	pxgrid_config_set_client_cert_chain_filename(config, hconfig->client_cert_chain_filename);
	pxgrid_config_set_client_cert_key_filename(config, hconfig->client_cert_key_filename);
	pxgrid_config_set_client_cert_key_password(config, hconfig->client_cert_key_password);
	pxgrid_config_set_server_cert_chain_filename(config, hconfig->server_cert_chain_filename);
	
	int i = 0;
	for (i = 0;i < nHosts; i++) 
	{
		free(hostnames[i]);
	}
        for (i = 0;i < nGroups; i++) 
	{
		free(groupnames[i]);
	}
	*_config = config;	
	return SUCCESS;
}
/*
int helper_config_connect(const helper_config * const hconfig, pxgrid_connection **_connection, pxgrid_config **_config) 
{
    pxgrid_config *config = NULL;
	pxgrid_connection *connection = NULL;	
		
	if( PXGRID_STATUS_OK != pxgrid_config_create(&config) )
	{
		printf("*** pxgrid_config_create failed\n");
		return FAILURE;	
	}
	char *hostnames[20];
	int nHosts =0 ;
	char *tf = NULL;
	tf = strtok(hconfig->host ," ");	
	while (tf != NULL)
	{
	    hostnames[nHosts] = (char*) calloc(strlen(tf)+1 , sizeof(char));
		strncpy(hostnames[nHosts] ,tf ,strlen(tf)+1 );	
	    tf = strtok (NULL," ");	 
	    nHosts++;
	}
	
	pxgrid_config_set_hosts(config, (const char **)hostnames , nHosts);
	pxgrid_config_set_user_name(config, hconfig->user_name);
	pxgrid_config_set_description(config, hconfig->description);
	pxgrid_config_set_client_cert_chain_filename(config, hconfig->client_cert_chain_filename);
	pxgrid_config_set_client_cert_key_filename(config, hconfig->client_cert_key_filename);
	pxgrid_config_set_client_cert_key_password(config, hconfig->client_cert_key_password);
	pxgrid_config_set_server_cert_chain_filename(config, hconfig->server_cert_chain_filename);
	
	int i = 0;
	for (;i < nHosts; i++) 
	{
		free(hostnames[i]);
	}
	
    
	if( PXGRID_STATUS_OK != pxgrid_connection_create(&connection) )
	{
		printf("*** pxgrid_connection_create failed\n");
		pxgrid_config_destroy(config);
		return FAILURE;	
	}
	pxgrid_connection_set_config(connection, config);
	pxgrid_connection_set_disconnect_cb(connection, _on_disconnected);	
	pxgrid_connection_set_connect_cb(connection, _on_connected);
    
    pxgrid_connection_set_ssl_ctx_cb(connection, (pxgrid_connection_ssl_ctx_cb)_user_ssl_ctx_cb);
    pxgrid_connection_set_ssl_ctx_cb_user_data(connection, (helper_config *)hconfig);	
	if(hconfig->is_reconnection_mode)
	{
		*_connection = connection;
		*_config = config;
		return SUCCESS;
	}   
    
	PXGRID_STATUS status = pxgrid_connection_connect(connection);
	if( PXGRID_STATUS_OK == status )
	{
		*_connection = connection;
		*_config = config;
		return SUCCESS;
	}
	else
	{
		printf("connection status=%s\n", pxgrid_status_get_message(status));		
		pxgrid_config_destroy(config);
		pxgrid_connection_destroy(connection);
	
		return FAILURE;		
	} 		
}*/
void helper_config_destroy(helper_config *hconfig) 
{
	if(hconfig) {
		if(hconfig->user_name) free(hconfig->user_name);
		if(hconfig->description) free(hconfig->description);
		if(hconfig->host) free(hconfig->host);
                if(hconfig->group) free(hconfig->group);
		if(hconfig->client_cert_chain_filename) free(hconfig->client_cert_chain_filename);
		if(hconfig->client_cert_key_filename) free(hconfig->client_cert_key_filename);
		if(hconfig->client_cert_key_password) free(hconfig->client_cert_key_password);
		if(hconfig->server_cert_chain_filename) free(hconfig->server_cert_chain_filename);
		if(hconfig->bulk_server_cert_chain_filename) free(hconfig->bulk_server_cert_chain_filename);
		if(hconfig->rest_host) free(hconfig->rest_host);
		if(hconfig->filter) free(hconfig->filter);
		if(hconfig->cap_name) free(hconfig->cap_name);
		if(hconfig->cap_version) free(hconfig->cap_version);
		if(hconfig->cap_query) free(hconfig->cap_query);
		if(hconfig->cap_action) free(hconfig->cap_action);
                if(hconfig->cap_description) free(hconfig->cap_description);
		if(hconfig->cap_vendorplatform) free(hconfig->cap_vendorplatform);
        free(hconfig);
	}
}

void ise_print_changetype(jw_dom_node *changetype_node)
{
	printf("Change Type:%s\n", jw_dom_get_first_text(changetype_node));
}

bool helper_prompt(const char *message, char *result) {
    printf("%s", message);
    if (result == NULL) {
        getchar();
        return true;
    }
    else {
        fgets(result, 128, stdin);
        // Remove newline char
        result[strlen(result) - 1] = '\0';
        if (strlen(result) > 0) return true;
    }
    return false;
}

void anc_action_prompt(int *actions_chosen) {
	char            action_name_str[16]        = {0};
    char            action_name_extra_str[16]  = {0};
    unsigned int    action_name                = END_POLICY_ACTION;
  	static const char *ACTION_ALREADY_SELECTED = "Action already selected. Please choose another.";

	//Write function prompt for action type
	do {
	printf("Enter policy action # (0 to stop adding): \n");
	printf ("0. EXIT\n");
	printf ("1. QUARANTINE\n");
	printf ("2. REMEDIATE\n");
	printf ("3. PROVISIONING\n");
	printf ("4. SHUT_DOWN\n");
	printf ("5. PORT_BOUNCE\n");
	printf ("Enter policy action #:");
	fgets(action_name_str, sizeof(action_name_str), stdin);
	sscanf(action_name_str, "%i%[^\n]", &action_name, action_name_extra_str);
	int i;
	int flag = 0;
	switch(action_name) {
	    case QUARANTINE:
	        if(actions_chosen[0] != 0) {
	            printf("%s\n", ACTION_ALREADY_SELECTED);
	        }
	        else {
	            actions_chosen[0] = QUARANTINE;
	        }
	        break;
	    case REMEDIATE:
	        if(actions_chosen[1] != 0) {
	            printf("%s\n", ACTION_ALREADY_SELECTED);
	        }
	        else {
	            actions_chosen[1] = REMEDIATE;
	        }
	        break;
	    case PROVISIONING:
	        if(actions_chosen[2] != 0) {
	            printf("%s\n", ACTION_ALREADY_SELECTED);
	        }
	        else {
	            actions_chosen[2] = PROVISIONING;
	        }

	        break;
	    case SHUT_DOWN:
	        if(actions_chosen[3] != 0) {
	            printf("%s\n", ACTION_ALREADY_SELECTED);
	        }
	        else {
	            actions_chosen[3] = SHUT_DOWN;
	        }
	        break;
	    case PORT_BOUNCE:
	        if(actions_chosen[4] != 0) {
	            printf("%s\n", ACTION_ALREADY_SELECTED);
	        }
	        else {
	            actions_chosen[4] = PORT_BOUNCE;
	        }
	        break;
	    case END_POLICY_ACTION:
	    	//Check user selected at least one option
	    	for(i = 0; i < NUM_ANC_ACTIONS; i++) {
	    		if(actions_chosen[i] != 0) {
	    			flag = 1;
	    		}
	    	}
	    	if(flag == 0) {
	    		printf("Please provide at least one action.");
	    		break;
	    	}
	    	else {
	    		action_name = END_POLICY_ACTION;
	    	}
	        break;
	    default:
	        printf("Please provide valid option.");
	        break;
	}
	} while(action_name != END_POLICY_ACTION);
}

static int _pem_key_password_cb(char *buf, int size, int rwflag, void *user_data) {
    UNUSED(rwflag);
    helper_connection *hconn = user_data;
    helper_config *hconfig = hconn->hconfig;
    strncpy(buf, hconfig->client_cert_key_password, size);
    buf[size - 1] = '\0';
    return (int)strlen(buf);
}

static void _user_ssl_ctx_cb(pxgrid_connection *connection, void *_ssl_ctx, void *user_data) {
    UNUSED(connection);
    helper_connection *hconn = user_data;
    helper_config *hconfig = hconn->hconfig;
    SSL_CTX *ssl_ctx = _ssl_ctx;
    
    printf("helper_ssl_ctx_cb called\n");
    SSL_CTX_set_default_passwd_cb(ssl_ctx, _pem_key_password_cb);
    SSL_CTX_set_default_passwd_cb_userdata(ssl_ctx, hconn);
    SSL_CTX_use_certificate_chain_file(ssl_ctx, hconfig->client_cert_chain_filename);
    SSL_CTX_use_PrivateKey_file(ssl_ctx, hconfig->client_cert_key_filename, SSL_FILETYPE_PEM);
    SSL_CTX_load_verify_locations(ssl_ctx, hconfig->server_cert_chain_filename, NULL);
    SSL_CTX_set_verify(ssl_ctx, SSL_VERIFY_PEER, NULL);
}

static void _on_disconnect(pxgrid_connection *connection, PXGRID_STATUS status, void *user_data) {
    UNUSED(connection);
    UNUSED(user_data);
    printf("_on_disconnect() status=%s\n", pxgrid_status_get_message(status));
}

static void _on_connect(pxgrid_connection *connection, void *user_data) {
    UNUSED(connection);
    UNUSED(user_data);
    printf("_on_connect()\n");
}

static void _on_account(pxgrid_connection *connection, PXGRID_STATUS status, void *user_data) {
    UNUSED(connection);
    UNUSED(user_data);
    printf("_on_account() status=%s\n", pxgrid_status_get_message(status));
}

void helper_connection_create(helper_connection **helper, int argc, char *argv[]) {
    *helper = malloc(sizeof(helper_connection));
    helper_config_create(&((*helper)->hconfig), argc, argv);
    
    pxgrid_config *config;
    helper_pxgrid_config_create((*helper)->hconfig , &config);
    (*helper)->conn_config = config;
    
    pxgrid_connection *connection;
    pxgrid_connection_create(&connection);
    (*helper)->connection = connection;
    
    // Set connection configuration data
    pxgrid_connection_set_config(connection, config);
    
    // Set callbacks
    pxgrid_connection_set_disconnect_cb(connection, _on_disconnect);
    pxgrid_connection_set_connect_cb(connection, _on_connect);
    pxgrid_connection_set_account_cb(connection, _on_account);
    pxgrid_connection_set_ssl_ctx_cb(connection, (pxgrid_connection_ssl_ctx_cb)_user_ssl_ctx_cb);
    pxgrid_connection_set_ssl_ctx_cb_user_data(connection, (helper_connection *)(*helper));
}

void helper_connection_connect(helper_connection *helper) {
    pxgrid_connection_connect(helper->connection);
}

void helper_connection_disconnect(helper_connection *helper) {
    pxgrid_connection_disconnect(helper->connection);
}

void helper_connection_destroy(helper_connection *helper) {
    pxgrid_connection_destroy(helper->connection);
    pxgrid_config_destroy(helper->conn_config);
    helper_config_destroy(helper->hconfig);
    free(helper);
}

pxgrid_connection *helper_connection_get_pxgrid_connection(helper_connection *helper) {
    return helper->connection;
}


bool helper_jw_dom_add_child_with_text(jw_dom_node *parent, const char *child_name, const char *text, jw_err *err) {
    jw_dom_ctx *ctx = jw_dom_get_context(parent);
    jw_dom_node *child_node;
    jw_dom_node_type *child_text;
    
    if(!jw_dom_element_create(ctx, child_name, &child_node, err)
       || !jw_dom_text_create(ctx, text, &child_text, err)
       || !jw_dom_add_child(child_node, child_text, err)
       || !jw_dom_add_child(parent, child_node, err)
       ) {
        return false;
    }
    return true;
}

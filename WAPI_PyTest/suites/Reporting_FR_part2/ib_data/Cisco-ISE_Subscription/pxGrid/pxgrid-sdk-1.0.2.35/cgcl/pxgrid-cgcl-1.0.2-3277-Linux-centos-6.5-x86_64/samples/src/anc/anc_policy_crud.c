#include <string.h>
#include "anc_policy_crud.h"


PXGRID_STATUS anc_createPolicyRequest(pxgrid_connection *connection, pxgrid_capability *capability, char *name, int *actions) {
    PXGRID_STATUS status = PXGRID_STATUS_OK;
    
    jw_err err;
    jw_dom_ctx_type *ctx;
    jw_dom_node *anc_policy;
    jw_dom_node *anc_policy_name;
    jw_dom_node *anc_policy_name_text;
    jw_dom_node *anc_policy_action;
    jw_dom_node *anc_policy_action_text;
    jw_dom_node *request;
    jw_dom_node *response;

    /*
    <createPolicyRequest xmlns='http://www.cisco.com/pxgrid/anc'>
        <policy>
            <name xmlns='http://www.cisco.com/pxgrid/anc/'>xGrid ANC Policy</name>
            <action xmlns='http://www.cisco.com/pxgrid/anc/'>Quarantine</action>
            <action xmlns='http://www.cisco.com/pxgrid/anc/policy'>Provisioning</action>
        </policy>
    </createPolicyRequest>
    */

    if (!jw_dom_context_create(&ctx, &err)
        || !jw_dom_element_create(ctx, "{http://www.cisco.com/pxgrid/anc}createPolicyRequest", &request, &err)
        || !jw_dom_element_create(ctx, "{http://www.cisco.com/pxgrid/anc}policy", &anc_policy, &err)
        || !jw_dom_add_child(request, anc_policy, &err)
        || !jw_dom_element_create(ctx, "{http://www.cisco.com/pxgrid/anc}name", &anc_policy_name, &err)
        || !jw_dom_add_child(anc_policy, anc_policy_name, &err)
        || !jw_dom_text_create(ctx, name, &anc_policy_name_text, &err)
        || !jw_dom_add_child(anc_policy_name, anc_policy_name_text, &err)
        )
    {
        jw_log_err(JW_LOG_ERROR, &err, "query");
        return PXGRID_STATUS_JW_ERROR;
    }

    char *action;
    int i;
    for(i = 0; i < NUM_ANC_ACTIONS; i++)
    {
        if(actions[i] == 0) {continue;}
        else if(actions[i] == QUARANTINE) { action = POLICY_ACTION_STRING[QUARANTINE];}
        else if(actions[i] == REMEDIATE) { action = POLICY_ACTION_STRING[REMEDIATE];}
        else if(actions[i] == PROVISIONING) { action = POLICY_ACTION_STRING[PROVISIONING];}
        else if(actions[i] == SHUT_DOWN) { action = POLICY_ACTION_STRING[SHUT_DOWN];}
        else if(actions[i] == PORT_BOUNCE) { action = POLICY_ACTION_STRING[PORT_BOUNCE];}
        if (!jw_dom_element_create(ctx, "{http://www.cisco.com/pxgrid/anc}action", &anc_policy_action, &err)
            || !jw_dom_add_child(anc_policy, anc_policy_action, &err)
            || !jw_dom_text_create(ctx, action, &anc_policy_action_text, &err)
            || !jw_dom_add_child(anc_policy_action, anc_policy_action_text, &err)) 
        {
            jw_log_err(JW_LOG_ERROR, &err, "query");
            return PXGRID_STATUS_JW_ERROR;
        }
    }

    printf("***request\n");
    helper_print_jw_dom(request);

    status = pxgrid_connection_query(connection, capability, request, &response);
    printf("status=%s\n", pxgrid_status_get_message(status));

    printf("***response\n");
    helper_print_jw_dom(response);

    if(ctx) jw_dom_context_destroy(ctx);

    return status;
}

PXGRID_STATUS anc_updatePolicyRequest(pxgrid_connection *connection, pxgrid_capability *capability, char *name, int *actions) {
    PXGRID_STATUS status = PXGRID_STATUS_OK;
    
    jw_err err;
    jw_dom_ctx_type *ctx;
    jw_dom_node *anc_policy;
    jw_dom_node *anc_policy_name;
    jw_dom_node *anc_policy_name_text;
    jw_dom_node *anc_policy_action;
    jw_dom_node *anc_policy_action_text;
    jw_dom_node *request;
    jw_dom_node *response;

    /*
    <updatePolicyRequest xmlns='http://www.cisco.com/pxgrid/anc'>
        <policy>
            <name xmlns='http://www.cisco.com/pxgrid/anc'>xGrid ANC Policy</name>
            <action xmlns='http://www.cisco.com/pxgrid/anc'>Quarantine</action>
            <action xmlns='http://www.cisco.com/pxgrid/anc'>Remediate</action>
        </policy>
    </updatePolicyRequest>
    */

    if (!jw_dom_context_create(&ctx, &err)
        || !jw_dom_element_create(ctx, "{http://www.cisco.com/pxgrid/anc}updatePolicyRequest", &request, &err)
        || !jw_dom_element_create(ctx, "{http://www.cisco.com/pxgrid/anc}policy", &anc_policy, &err)
        || !jw_dom_add_child(request, anc_policy, &err)
        || !jw_dom_element_create(ctx, "{http://www.cisco.com/pxgrid/anc}name", &anc_policy_name, &err)
        || !jw_dom_add_child(anc_policy, anc_policy_name, &err)
        || !jw_dom_text_create(ctx, name, &anc_policy_name_text, &err)
        || !jw_dom_add_child(anc_policy_name, anc_policy_name_text, &err)
        )
    {
        jw_log_err(JW_LOG_ERROR, &err, "query");
        return PXGRID_STATUS_JW_ERROR;
    }

    char *action;
    int i;
    for(i = 0; i < NUM_ANC_ACTIONS; i++)
    {
        if(actions[i] == 0) {continue;}
        else if(actions[i] == QUARANTINE) { action = POLICY_ACTION_STRING[QUARANTINE];}
        else if(actions[i] == REMEDIATE) { action = POLICY_ACTION_STRING[REMEDIATE];}
        else if(actions[i] == PROVISIONING) { action = POLICY_ACTION_STRING[PROVISIONING];}
        else if(actions[i] == SHUT_DOWN) { action = POLICY_ACTION_STRING[SHUT_DOWN];}
        else if(actions[i] == PORT_BOUNCE) { action = POLICY_ACTION_STRING[PORT_BOUNCE];}
        if (!jw_dom_element_create(ctx, "{http://www.cisco.com/pxgrid/anc}action", &anc_policy_action, &err)
            || !jw_dom_add_child(anc_policy, anc_policy_action, &err)
            || !jw_dom_text_create(ctx, action, &anc_policy_action_text, &err)
            || !jw_dom_add_child(anc_policy_action, anc_policy_action_text, &err)) 
        {
            jw_log_err(JW_LOG_ERROR, &err, "query");
            return PXGRID_STATUS_JW_ERROR;
        }
        action = strtok (NULL, ",");
    }

    printf("***request\n");
    helper_print_jw_dom(request);

    status = pxgrid_connection_query(connection, capability, request, &response);
    printf("status=%s\n", pxgrid_status_get_message(status));

    printf("***response\n");
    helper_print_jw_dom(response);

    if(ctx) jw_dom_context_destroy(ctx);

    return status;
}

PXGRID_STATUS anc_deletePolicyRequest(pxgrid_connection *connection, pxgrid_capability *capability, char * name) {
    PXGRID_STATUS status = PXGRID_STATUS_OK;

    jw_err err;
    jw_dom_ctx_type *ctx;
    jw_dom_node *anc_policy_name;
    jw_dom_node *anc_policy_name_text;
    jw_dom_node *request;
    jw_dom_node *response;

    /*
    <deletePolicyRequest xmlns='http://www.cisco.com/pxgrid/anc'>
        <name xmlns='http://www.cisco.com/pxgrid/anc'>xGridANCpolicy</name>
    </deletePolicyRequest>
    */

    if (!jw_dom_context_create(&ctx, &err)
        || !jw_dom_element_create(ctx, "{http://www.cisco.com/pxgrid/anc}deletePolicyRequest", &request, &err)
        || !jw_dom_element_create(ctx, "{http://www.cisco.com/pxgrid/anc}name", &anc_policy_name, &err)
        || !jw_dom_add_child(request, anc_policy_name, &err)
        || !jw_dom_text_create(ctx, name, &anc_policy_name_text, &err)
        || !jw_dom_add_child(anc_policy_name, anc_policy_name_text, &err)
        )
    {
        jw_log_err(JW_LOG_ERROR, &err, "query");
        return PXGRID_STATUS_JW_ERROR;
    }

    printf("***request\n");
    helper_print_jw_dom(request);

    status = pxgrid_connection_query(connection, capability, request, &response);
    printf("status=%s\n", pxgrid_status_get_message(status));

    printf("***response\n");
    helper_print_jw_dom(response);

    if(ctx) jw_dom_context_destroy(ctx);
    return status;
}

PXGRID_STATUS anc_getPolicyByName(pxgrid_connection *connection, pxgrid_capability *capability, char *name) {
    PXGRID_STATUS status = PXGRID_STATUS_OK;

    jw_err err;
    jw_dom_ctx_type *ctx;
    jw_dom_node *anc_policy_name;
    jw_dom_node *anc_policy_name_text;
    jw_dom_node *request;
    jw_dom_node *response;

    /*
    <getPolicyByNameRequest xmlns='http://www.cisco.com/pxgrid/anc'>
        <name xmlns='http://www.cisco.com/pxgrid/anc'>xGridANCpolicy</name>
    </getPolicyByNameRequest>
    */

    if (!jw_dom_context_create(&ctx, &err)
        || !jw_dom_element_create(ctx, "{http://www.cisco.com/pxgrid/anc}getPolicyByNameRequest", &request, &err)
        || !jw_dom_element_create(ctx, "{http://www.cisco.com/pxgrid/anc}name", &anc_policy_name, &err)
        || !jw_dom_add_child(request, anc_policy_name, &err)
        || !jw_dom_text_create(ctx, name, &anc_policy_name_text, &err)
        || !jw_dom_add_child(anc_policy_name, anc_policy_name_text, &err)
        )
    {
        jw_log_err(JW_LOG_ERROR, &err, "query");
        return PXGRID_STATUS_JW_ERROR;
    }

    printf("***request\n");
    helper_print_jw_dom(request);

    status = pxgrid_connection_query(connection, capability, request, &response);
    printf("status=%s\n", pxgrid_status_get_message(status));

    printf("***response\n");
    helper_print_jw_dom(response);

    if(ctx) jw_dom_context_destroy(ctx);

    return status;
}

PXGRID_STATUS anc_getAllPolicies(pxgrid_connection *connection, pxgrid_capability *capability) {
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
        jw_log_err(JW_LOG_ERROR, &err, "query");
        return PXGRID_STATUS_JW_ERROR;
    }

    printf("***request\n");
    helper_print_jw_dom(request);

    status = pxgrid_connection_query(connection, capability, request, &response);
    printf("status=%s\n", pxgrid_status_get_message(status));

    printf("***response\n");
    helper_print_jw_dom(response);

    if(ctx) jw_dom_context_destroy(ctx);

    return status;
}

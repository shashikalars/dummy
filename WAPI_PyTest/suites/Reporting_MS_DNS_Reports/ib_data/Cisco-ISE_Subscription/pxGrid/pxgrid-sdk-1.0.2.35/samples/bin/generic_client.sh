#!/bin/bash

SCRIPT_BIN_DIR=$(dirname $0)
source $SCRIPT_BIN_DIR/common.sh

common_setup $*

PXGRID_GROUP="BASIC"
common_run -Dtopic-name="$GENERIC_TOPIC_NAME" \
           -Dclient-mode="$GENERIC_CLIENT_MODE" \
           -Dquery-name-set="$GENERIC_QUERY_NAME_SET" \
           -Daction-name-set="$GENERIC_ACTION_NAME_SET" \
           -Dpublish-data-set="$GENERIC_PUBLISH_DATA_SET" \
           -Drequest-data-set="$GENERIC_REQUEST_DATA_SET" \
           -Dresponse-data-set="$GENERIC_RESPONSE_DATA_SET" \
           -Dsleep-interval="$GENERIC_SLEEP_INTERVAL" \
           -Diterations="$GENERIC_ITERATIONS" \
           com.cisco.pxgrid.samples.ise.GenericClient

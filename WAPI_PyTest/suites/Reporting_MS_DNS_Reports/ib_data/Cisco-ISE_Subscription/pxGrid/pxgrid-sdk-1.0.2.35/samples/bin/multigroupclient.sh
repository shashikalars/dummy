#!/bin/bash

SCRIPT_BIN_DIR=$(dirname $0)
source $SCRIPT_BIN_DIR/common.sh

common_setup $*

PXGRID_GROUP="Session,ANC,$PXGRID_GROUP"
common_run -DPOLICY_NAME="$POLICY_NAME" \
           -DSESSION_IP="$SESSION_IP" \
           com.cisco.pxgrid.samples.ise.MultiGroupClient

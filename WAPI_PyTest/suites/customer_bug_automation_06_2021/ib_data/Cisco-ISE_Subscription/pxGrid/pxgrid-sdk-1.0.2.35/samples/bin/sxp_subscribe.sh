#!/bin/bash

SCRIPT_BIN_DIR=$(dirname $0)
source $SCRIPT_BIN_DIR/common.sh

common_setup $*

PXGRID_GROUP="Session"
common_run com.cisco.pxgrid.samples.ise.SXPBindingSubscribe

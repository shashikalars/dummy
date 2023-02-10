#!/bin/bash

SCRIPT_BIN_DIR=$(dirname $0)
source $SCRIPT_BIN_DIR/common.sh

common_setup $*

PXGRID_GROUP="EPS"
common_run com.cisco.pxgrid.samples.ise.EPSQuarantine

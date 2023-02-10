#!/bin/bash


if [ "$JAVA_HOME" == "" ]
then
    echo "must set JAVA_HOME (export JAVA_HOME=<path to your JRE>)"
    exit 1
fi

if [ ! -f $JAVA_HOME/bin/java ]; then
    echo "unable to find bin/java in JAVA_HOME"
    exit 1
fi

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SAMPLES_LIB_DIR="$SCRIPT_DIR/../lib"
SAMPLES_HOME_DIR="$SCRIPT_DIR/.."
SAMPLES_PROPERTIES_FILE="$SAMPLES_HOME_DIR/conf/samples.properties"
SDK_LIB_DIR="$SCRIPT_DIR/../../lib"
LOG_CONFIG="$SCRIPT_DIR/../conf/logback.xml"

$JAVA_HOME/bin/java -cp .:"$SDK_LIB_DIR"/*:"$SAMPLES_LIB_DIR"/* -Dhttps.protocols="TLSv1" -Dlogback.configurationFile="$LOG_CONFIG" -DsamplesHome="$SAMPLES_HOME_DIR" -DsamplesProperties="$SAMPLES_PROPERTIES_FILE" -DsamplesVersion="1.0.0.10" com.cisco.pxgrid.samples.ise.UserIdentityGroupDownload $*

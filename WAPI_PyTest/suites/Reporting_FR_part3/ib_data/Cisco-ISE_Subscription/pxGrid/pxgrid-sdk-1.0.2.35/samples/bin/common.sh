#!/bin/bash

function print_help {
    echo "Usage: $0 [options]"
    echo
    echo "  Main options"
    echo "    -a <PXGRID_HOSTNAMES> (comma separated hostnames)"
    echo "    -u <PXGRID_USERNAME>"
    echo "    -g <PXGRID_GROUP>"
    echo "    -d <PXGRID_DESCRIPTION>"
    echo
    echo "  The followings are certificates options"
    echo "    -k <PXGRID_KEYSTORE_FILENAME>"
    echo "    -p <PXGRID_KEYSTORE_PASSWORD>"
    echo "    -t <PXGRID_TRUSTSTORE_FILENAME>"
    echo "    -q <PXGRID_TRUSTSTORE_PASSWORD>"
    echo "  If not specified, it defaults to use clientSample1.jks and rootSample.jks"
    echo "  Specifying values here can override the defaults"
    echo
    echo "  Custom config file can fill or override parameters"
    echo "    -c <config_filename>"
    echo "  Config file are being sourced. Use these variables:"
    echo "        PXGRID_HOSTNAMES"
    echo "        PXGRID_USERNAME"
    echo "        PXGRID_GROUP"
    echo "        PXGRID_DESCRIPTION"
    echo "        PXGRID_KEYSTORE_FILENAME"
    echo "        PXGRID_KEYSTORE_PASSWORD"
    echo "        PXGRID_TRUSTSTORE_FILENAME"
    echo "        PXGRID_TRUSTSTORE_PASSWORD"
    
}

function common_setup {
    if [ "$JAVA_HOME" == "" ]; then
      echo "JAVA_HOME is not set"
      exit 1
    fi

    SAMPLE_BIN_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
    SAMPLE_ROOT_DIR="$(dirname $SAMPLE_BIN_DIR)"
    SAMPLE_LIB_DIR="$SAMPLE_ROOT_DIR/lib"
    SDK_ROOT_DIR="$(dirname $SAMPLE_ROOT_DIR)"
    SDK_LIB_DIR="$SDK_ROOT_DIR/lib"
    LOG_CONFIG="$SAMPLE_ROOT_DIR/conf/logback.xml"
    
    # Default client configurations
    PXGRID_KEYSTORE_FILENAME=$SAMPLE_ROOT_DIR/certs/clientSample1.jks
    PXGRID_KEYSTORE_PASSWORD=cisco123
    PXGRID_TRUSTSTORE_FILENAME=$SAMPLE_ROOT_DIR/certs/rootSample.jks
    PXGRID_TRUSTSTORE_PASSWORD=cisco123

    while getopts "a:u:g:d:c:k:p:t:q:?:c" opt; do
      case $opt in
        a) PXGRID_HOSTNAMES=$OPTARG;;
        u) PXGRID_USERNAME=$OPTARG;;
        g) PXGRID_GROUP=$OPTARG;;
        d) PXGRID_DESCRIPTION=$OPTARG;;
        k) PXGRID_KEYSTORE_FILENAME=$OPTARG;;
        p) PXGRID_KEYSTORE_PASSWORD=$OPTARG;;
        t) PXGRID_TRUSTSTORE_FILENAME=$OPTARG;;
        q) PXGRID_TRUSTSTORE_PASSWORD=$OPTARG;;
        c) SAMPLE_CONFIG_FILENAME=$OPTARG;;
        ?) print_help; exit 1;;
      esac
    done
  
    if [ "$SAMPLE_CONFIG_FILENAME" != "" ]; then
        source $SAMPLE_CONFIG_FILENAME
    fi
}

function common_run {
  $JAVA_HOME/bin/java \
    -cp .:"$SDK_LIB_DIR"/*:"$SAMPLE_LIB_DIR"/* \
    -Dlogback.configurationFile="$LOG_CONFIG" \
    -DPXGRID_HOSTNAMES="$PXGRID_HOSTNAMES" \
    -DPXGRID_USERNAME="$PXGRID_USERNAME" \
    -DPXGRID_GROUP="$PXGRID_GROUP" \
    -DPXGRID_DESCRIPTION="$PXGRID_DESCRIPTION" \
    -DPXGRID_KEYSTORE_FILENAME="$PXGRID_KEYSTORE_FILENAME" \
    -DPXGRID_KEYSTORE_PASSWORD="$PXGRID_KEYSTORE_PASSWORD" \
    -DPXGRID_TRUSTSTORE_FILENAME="$PXGRID_TRUSTSTORE_FILENAME" \
    -DPXGRID_TRUSTSTORE_PASSWORD="$PXGRID_TRUSTSTORE_PASSWORD" \
    $*
}

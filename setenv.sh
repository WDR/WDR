#!/bin/bash

. $WDR_HOME/runtimes.default.sh

if [[ -f $WDR_HOME/runtimes.sh ]] ; then
	. $WDR_HOME/runtimes.sh
fi

case ${WAS_RUNTIME} in
was61_client | was61)
	WAS_HOME=$WAS61_RUNTIME_HOME
	WSADMIN_CLASS_PATH=${WAS_HOME}/optionalLibrariesjython/jython.jar:${WAS_HOME}/plugins/com.ibm.ws.security.crypto_6.1.0.jar:${WAS_HOME}/runtimes/com.ibm.ws.admin.client_6.1.0.jar
	RUNTIME_NAME=was61
was7_client | was70_client | was7 | was70)
	WAS_HOME=$WAS70_RUNTIME_HOME
	WSADMIN_CLASS_PATH=${WAS_HOME}/optionalLibrariesjython/jython.jar:${WAS_HOME}/runtimes/com.ibm.ws.admin.client_7.0.0.jar:${WAS_HOME}/plugins/com.ibm.ws.security.crypto.jar
	RUNTIME_NAME=was7
was8_client | was80_client | was8 | was80)
	WAS_HOME=$WAS80_RUNTIME_HOME
	WSADMIN_CLASS_PATH=${WAS_HOME}/optionalLibrariesjython/jython.jar:${WAS_HOME}/runtimes/com.ibm.ws.admin.client_8.0.0.jar:${WAS_HOME}/plugins/com.ibm.ws.security.crypto.jar
	RUNTIME_NAME=was80
was85_client | was85_client | was85 | was85)
	WAS_HOME=$WAS85_RUNTIME_HOME
	WSADMIN_CLASS_PATH=${WAS_HOME}/optionalLibrariesjython/jython.jar:${WAS_HOME}/runtimes/com.ibm.ws.admin.client_8.5.0.jar:${WAS_HOME}/plugins/com.ibm.ws.security.crypto.jar
	RUNTIME_NAME=was85
*)
	echo "Unknown WAS runtime: ${WAS_RUNTIME}" >&2
	exit 1
esac

if [[ ! -f ${WAS_HOME}/bin/ws_ant.sh ]] ; then
	echo "WAS runtime ${WAS_RUNTIME} points to ${WAS_HOME} which does not seem to be a valid WAS runtime" >&2
	exit 1
fi

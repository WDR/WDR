#!/bin/bash

#
# Copyright 2012-2015 Marcin Plonka <mplonka@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

. $WDR_HOME/runtimes.default.sh

if [[ -f $WDR_HOME/runtimes.sh ]] ; then
	. $WDR_HOME/runtimes.sh
fi

case ${WAS_RUNTIME} in
was61_client | was61)
	WAS_HOME=$WAS61_RUNTIME_HOME
	WSADMIN_CLASS_PATH=${WAS_HOME}/optionalLibraries/jython/jython.jar:${WAS_HOME}/plugins/com.ibm.ws.security.crypto_6.1.0.jar:${WAS_HOME}/runtimes/com.ibm.ws.admin.client_6.1.0.jar
	JYTHON_VERSION=$WAS61_JYTHON_VERSION
	RUNTIME_NAME=was61
	;;
was7_client | was70_client | was7 | was70)
	WAS_HOME=$WAS70_RUNTIME_HOME
	WSADMIN_CLASS_PATH=${WAS_HOME}/optionalLibraries/jython/jython.jar:${WAS_HOME}/runtimes/com.ibm.ws.admin.client_7.0.0.jar:${WAS_HOME}/plugins/com.ibm.ws.security.crypto.jar
	JYTHON_VERSION=$WAS70_JYTHON_VERSION
	RUNTIME_NAME=was7
	;;
was8_client | was80_client | was8 | was80)
	WAS_HOME=$WAS80_RUNTIME_HOME
	WSADMIN_CLASS_PATH=${WAS_HOME}/optionalLibraries/jython/jython.jar:${WAS_HOME}/runtimes/com.ibm.ws.admin.client_8.0.0.jar:${WAS_HOME}/plugins/com.ibm.ws.security.crypto.jar
	JYTHON_VERSION=$WAS80_JYTHON_VERSION
	RUNTIME_NAME=was80
	;;
was85_client | was85_client | was85 | was85)
	WAS_HOME=$WAS85_RUNTIME_HOME
	WSADMIN_CLASS_PATH=${WAS_HOME}/optionalLibraries/jython/jython.jar:${WAS_HOME}/runtimes/com.ibm.ws.admin.client_8.5.0.jar:${WAS_HOME}/plugins/com.ibm.ws.security.crypto.jar
	JYTHON_VERSION=$WAS85_JYTHON_VERSION
	RUNTIME_NAME=was85
	;;
*)
	echo "Unknown WAS runtime: ${WAS_RUNTIME}" >&2
	exit 1
esac

if [[ ! -f ${WAS_HOME}/bin/ws_ant.sh ]] ; then
	echo "WAS runtime ${WAS_RUNTIME} points to ${WAS_HOME} which does not seem to be a valid WAS runtime" >&2
	exit 1
fi

#!/bin/sh

WDR_HOME=`dirname $0`
WAS_DEBUG=""

WAS_RUNTIME=$1
shift
TARGET_ENV=$1
shift
SCRIPT=$1
shift

. $WDR_HOME/setenv.sh

WAS_LOGGING_PROPERTIES="-Djava.util.logging.manager=com.ibm.ws.bootstrap.WsLogManager -Djava.util.logging.configureByServer=true"
THIN_CLIENT_PROPERTY="-Dcom.ibm.websphere.thinclient=true"
CONSOLE_ENCODING_PROPERTY="-Dws.output.encoding=console"
APP_TIMEOUT_PROPERTY="-Dcom.ibm.ws.scripting.apptimeout=1800"
SHELL="com.ibm.ws.scripting.WasxShell"
PERFJAVAOPTIONS="-Xms128m -Xmx512m -Xj9 -Xquickstart"

JYTHON_CACHEDIR="-Dpython.cachedir=${HOME}/.wdr/cache/${RUNTIME_NAME}"
TMPDIR_PROPERTY=-Djava.io.tmpdir=${HOME}/.wdr/tmp/${TARGET_ENV}
WORKSPACE_PROPERTY=-Dwebsphere.workspace.root=${HOME}/.wdr/wstemp/${TARGET_ENV}

USER_ROOT="${HOME}/.wdr/environments/${TARGET_ENV}"
WSADMIN_PROPERTIES="${USER_ROOT}/wsadmin.properties"
SOAP_PROPERTIES="${USER_ROOT}/soap.properties"
SSL_CLIENT_PROPS="${USER_ROOT}/ssl.client.props"

if [[ ! -d ${USER_ROOT} ]] ; then
	echo "Environment ${TARGET_ENV} does not exist" >&2
	exit 1
fi

if [[ ! -f ${WSADMIN_PROPERTIES} || ! -f ${SOAP_PROPERTIES} || ! -f ${SSL_CLIENT_PROPS} ]] ; then
	echo "Environment ${TARGET_ENV} configuration is incomplete" >&2
	if [[ ! -f ${WSADMIN_PROPERTIES} ]] ; then
		echo "${WSADMIN_PROPERTIES} not found" >&2
	fi
	if [[ ! -f ${SOAP_PROPERTIES} ]] ; then
		echo "${SOAP_PROPERTIES} not found" >&2
	fi
	if [[ ! -f ${SSL_CLIENT_PROPS} ]] ; then
		echo "${SSL_CLIENT_PROPS} not found" >&2
	fi
	exit 1
fi

USER_ROOT_PROPERTY="-Duser.root=${USER_ROOT}"
WSADMIN_PROPERTIES_PROPERTY="-Dcom.ibm.ws.scripting.wsadminprops=${WSADMIN_PROPERTIES}"
SOAP_PROPERTIES_PROPERTY="-Dcom.ibm.SOAP.ConfigURL=file://${SOAP_PROPERTIES}"
SSL_CLIENT_PROPS_PROPERTY="-Dcom.ibm.SSL.ConfigURL=file://${SSL_CLIENT_PROPS}"
if [ "${CUSTOM_PROFILE}" == "" ]; then
	WDR_PROFILE_PROPERTY="-Dcom.ibm.ws.scripting.profiles=${WDR_HOME}/profile.py"
else
	WDR_PROFILE_PROPERTY="-Dcom.ibm.ws.scripting.profiles=${WDR_HOME}/profile.py:${CUSTOM_PROFILE}"
fi

# required to activate fix PM80400
# see: http://www-01.ibm.com/support/docview.wss?uid=swg1PM80400
WSADMIN_EXCEPTION_PROPAGATION="-Dcom.ibm.ws.scripting.exceptionPropagation=thrown"

WSADMIN_TRACE_STRING="-Dcom.ibm.ws.scripting.traceString=com.ibm.*=all=disabled"

PYTHON_PATH="-Dpython.path=${WAS_HOME}/optionalLibraries/jython/Lib:${WDR_HOME}/lib/common"

if [ "${JYTHON_VERSION}" == "2.1" ]; then
	PYTHON_PATH="${PYTHON_PATH}:${WDR_HOME}/lib/legacy"
fi

if [[ -d ${HOME}/.wdr/lib ]] ; then
	for lib in `find ${HOME}/.wdr/lib -mindepth 1 -maxdepth 1 -type d` ; do
		PYTHON_PATH=${PYTHON_PATH}:${lib}
	done
fi

if [ "${EXTRA_PYTHON_PATH}" != "" ]; then
	PYTHON_PATH="${PYTHON_PATH}:${EXTRA_PYTHON_PATH}"
fi

if [ "${TARGET_ENV}" == "" ]; then
	echo 'Usage:'
	echo 'wdr.sh environment [script]'
else
	if [ "${SCRIPT}" == "" ]; then
		rlwrap=`which rlwrap`
		${rlwrap} ${JAVA_HOME}/bin/java ${WSADMIN_TRACE_STRING} ${USER_ROOT_PROPERTY} ${PYTHON_PATH} ${JYTHON_CACHEDIR} ${TMPDIR_PROPERTY} ${WORKSPACE_PROPERTY} ${WSADMIN_EXCEPTION_PROPAGATION} ${WDR_PROFILE_PROPERTY} ${SOAP_PROPERTIES_PROPERTY} ${SSL_CLIENT_PROPS_PROPERTY} ${WAS_DEBUG} ${CONSOLE_ENCODING_PROPERTY} ${APP_TIMEOUT_PROPERTY} ${WAS_LOGGING_PROPERTIES} ${THIN_CLIENT_PROPERTY} ${PERFJAVAOPTIONS} ${WSADMIN_PROPERTIES_PROPERTY} -Duser.install.root=${WAS_HOME} -Dwas.install.root=${WAS_HOME} -cp ${WSADMIN_CLASS_PATH} ${SHELL} $*
	else
		${JAVA_HOME}/bin/java ${WSADMIN_TRACE_STRING} ${USER_ROOT_PROPERTY} ${PYTHON_PATH} ${JYTHON_CACHEDIR} ${TMPDIR_PROPERTY} ${WORKSPACE_PROPERTY} ${WSADMIN_EXCEPTION_PROPAGATION} ${WDR_PROFILE_PROPERTY} ${SOAP_PROPERTIES_PROPERTY} ${SSL_CLIENT_PROPS_PROPERTY} ${WAS_DEBUG} ${CONSOLE_ENCODING_PROPERTY} ${APP_TIMEOUT_PROPERTY} ${WAS_LOGGING_PROPERTIES} ${THIN_CLIENT_PROPERTY} ${PERFJAVAOPTIONS} ${WSADMIN_PROPERTIES_PROPERTY} -Duser.install.root=${WAS_HOME} -Dwas.install.root=${WAS_HOME} -cp ${WSADMIN_CLASS_PATH} ${SHELL} -f ${SCRIPT} $*
	fi
fi

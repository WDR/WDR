#!/bin/bash



err() {
    echo $* 1>&2
}


usage() {
    err Usage:
    err wdr environment [script] [script-args]
}


file_runtimes() {
    err '######################################################################'
    err '##       Runtime setup using runtimes.sh is deprecated              ##'
    err '##           and will be removed in the next version                ##'
    err '######################################################################'

    . $WDR_HOME/runtimes.default.sh
    . $WDR_HOME/runtimes.sh

    case ${WAS_RUNTIME} in
    was61_client | was61)
        RUNTIME_NAME=was61
        ;;
    was7_client | was70_client | was7 | was70)
        RUNTIME_NAME=was7
        ;;
    was8_client | was80_client | was8 | was80)
        RUNTIME_NAME=was80
        ;;
    was85_client | was85)
        RUNTIME_NAME=was85
        ;;
    was855_client | was855)
        RUNTIME_NAME=was855
        ;;
    was90_client | was90)
        RUNTIME_NAME=was90
        ;;
    esac


    if [ "$WAS_RUNTIME" == "was61" ] ; then
        WAS_HOME=$WAS61_RUNTIME_HOME
        WAS_JAVA_HOME=$WAS61_JAVA_HOME
        WSADMIN_CLASS_PATH=${WAS61_RUNTIME_HOME}/runtimes/com.ibm.ws.admin.client_6.1.0.jar:${WAS61_RUNTIME_HOME}/plugins/com.ibm.ws.security.crypto_6.1.0.jar
        JYTHON_VERSION=$WAS61_JYTHON_VERSION
    elif [ "$WAS_RUNTIME" == "was70" ] ; then
        WAS_HOME=$WAS70_RUNTIME_HOME
        WAS_JAVA_HOME=$WAS70_JAVA_HOME
        WSADMIN_CLASS_PATH=${WAS70_RUNTIME_HOME}/runtimes/com.ibm.ws.admin.client_7.0.0.jar:${WAS70_RUNTIME_HOME}/plugins/com.ibm.ws.security.crypto.jar
        JYTHON_VERSION=$WAS70_JYTHON_VERSION
    elif [ "$WAS_RUNTIME" == "was80" ] ; then
        WAS_HOME=$WAS80_RUNTIME_HOME
        WAS_JAVA_HOME=$WAS80_JAVA_HOME
        WSADMIN_CLASS_PATH=${WAS80_JAVA_HOME}/runtimes/com.ibm.ws.admin.client_8.0.0.jar:${WAS80_JAVA_HOME}/plugins/com.ibm.ws.security.crypto.jar
        JYTHON_VERSION=$WAS80_JYTHON_VERSION
    elif [ "$WAS_RUNTIME" == "was85" ] ; then
        WAS_HOME=$WAS85_RUNTIME_HOME
        WAS_JAVA_HOME=$WAS85_JAVA_HOME
        WSADMIN_CLASS_PATH=${WAS85_RUNTIME_HOME}/runtimes/com.ibm.ws.admin.client_8.5.0.jar:${WAS85_RUNTIME_HOME}/plugins/com.ibm.ws.security.crypto.jar
        JYTHON_VERSION=$WAS85_JYTHON_VERSION
    elif [ "$WAS_RUNTIME" == "was855" ] ; then
        WAS_HOME=$WAS855_RUNTIME_HOME
        WAS_JAVA_HOME=$WAS855_JAVA_HOME
        WSADMIN_CLASS_PATH=${WAS855_RUNTIME_HOME}/runtimes/com.ibm.ws.admin.client_8.5.0.jar:${WAS855_RUNTIME_HOME}/plugins/com.ibm.ws.security.crypto.jar
        JYTHON_VERSION=$WAS85_JYTHON_VERSION
    elif [ "$WAS_RUNTIME" == "was90" ] ; then
        WAS_HOME=$WAS90_RUNTIME_HOME
        WAS_JAVA_HOME=$WAS90_JAVA_HOME
        WSADMIN_CLASS_PATH=${WAS90_RUNTIME_HOME}/runtimes/com.ibm.ws.admin.client_9.0.jar:${WAS90_RUNTIME_HOME}/plugins/com.ibm.ws.security.crypto.jar
        JYTHON_VERSION=$WAS90_JYTHON_VERSION
    else
        err Unknown runtime $WAS_RUNTIME
        return 1
    fi
    return 0
}

dir_runtimes() {
    if [[ -f ${HOME}/.wdr/runtimes/${WAS_RUNTIME}.sh ]] ; then
        . ${HOME}/.wdr/runtimes/${WAS_RUNTIME}.sh
    elif [[ -f ${WDR_HOME}/runtimes/${WAS_RUNTIME}.sh ]] ; then
        . ${WDR_HOME}/runtimes/${WAS_RUNTIME}.sh
    elif [[ -f ${WDR_HOME}/runtimes.default/${WAS_RUNTIME}.sh ]] ; then
        . ${WDR_HOME}/runtimes.default/${WAS_RUNTIME}.sh
    else
        err Unknown WAS runtime: ${WAS_RUNTIME}
        return 1
    fi
    return 0
}

runtimes() {
    if [ -f ${WDR_HOME}/runtimes.sh ] ; then
        file_runtimes || return 1
    else
        dir_runtimes || return 1
    fi
    if [ "${WAS_JAVA_HOME}" == "" ] ; then
        WAS_JAVA_HOME=${WAS_HOME}/java
    fi
    return 0
}

setup() {
    runtimes || return 1
    JAVA_HOME=${WAS_JAVA_HOME}
    WSADMIN_CLASS_PATH=${WSADMIN_CLASS_PATH}
    JYTHON_VERSION=${JYTHON_VERSION}

    if [ "${PERFJAVAOPTIONS}" == "" ]; then
        PERFJAVAOPTIONS="-Xms128m -Xmx512m -Xj9 -Xquickstart"
    fi

    JYTHON_CACHEDIR=${HOME}/.wdr/cache/${RUNTIME_NAME}
    TMPDIR=${HOME}/.wdr/tmp/${TARGET_ENV}
    WORKSPACE=${HOME}/.wdr/wstemp/${TARGET_ENV}

    USER_ROOT=${HOME}/.wdr/environments/${TARGET_ENV}
    WSADMIN_PROPERTIES=${USER_ROOT}/wsadmin.properties
    SOAP_PROPERTIES=${USER_ROOT}/soap.properties
    SSL_CLIENT_PROPS=${USER_ROOT}/ssl.client.props

    if [[ ! -d ${USER_ROOT} ]] ; then
        err Environment ${TARGET_ENV} does not exist
        return 1
    else
        if [[ ! -f ${WSADMIN_PROPERTIES} ]] ; then
            err Environment ${TARGET_ENV} is incomplete
            err ${WSADMIN_PROPERTIES} not found
            return 1
        fi
        if [[ ! -f ${SOAP_PROPERTIES} ]] ; then
            err Environment ${TARGET_ENV} is incomplete
            err ${SOAP_PROPERTIES} not found
            return 1
        fi
        if [[ ! -f ${SSL_CLIENT_PROPS} ]] ; then
            err Environment ${TARGET_ENV} is incomplete
            err ${SSL_CLIENT_PROPS} not found
            return 1
        fi
    fi

    if [ "${CUSTOM_PROFILE}" == "" ] ; then
        WDR_PROFILE=${WDR_HOME}/profile.py
    else
        WDR_PROFILE=${WDR_HOME}/profile.py:${CUSTOM_PROFILE}
    fi

    PYTHON_PATH=${WDR_HOME}/lib/common
    if [ "${JYTHON_VERSION}" == "2.1" ]; then
        USE_JYTHON_21=true
        PYTHON_PATH="${PYTHON_PATH}:${WDR_HOME}/lib/legacy"
    else
        USE_JYTHON_21=false
    fi

    if [[ -d ${HOME}/.wdr/lib ]] ; then
        for lib in ${HOME}/.wdr/lib/* ; do PYTHON_PATH=${PYTHON_PATH}:${lib} ; done
    fi

    if [ "${EXTRA_PYTHON_PATH}" != "" ] ; then
        PYTHON_PATH="${PYTHON_PATH}:${EXTRA_PYTHON_PATH}"
    fi

    rlwrap=`which rlwrap 2>/dev/null`
    return 0
}

run_interactive() {
    ${rlwrap} ${JAVA_HOME}/jre/bin/java \
        "-Dcom.ibm.ws.scripting.defaultLang=jython" \
        "-Dcom.ibm.ws.scripting.usejython21=${USE_JYTHON_21}" \
        "-Dcom.ibm.ws.scripting.traceString=com.ibm.*=all=disabled" \
        "-Duser.root=${USER_ROOT}" \
        "-Dpython.path=${PYTHON_PATH}" \
        "-Dpython.cachedir=${JYTHON_CACHEDIR}" \
        "-Djava.io.tmpdir=${TMPDIR}" \
        "-Dwebsphere.workspace.root=${WORKSPACE}" \
        "-Dcom.ibm.ws.scripting.profiles=${WDR_PROFILE}" \
        "-Dcom.ibm.SOAP.ConfigURL=file://${SOAP_PROPERTIES}" \
        "-Dcom.ibm.SSL.ConfigURL=file://${SSL_CLIENT_PROPS}" \
        ${WAS_DEBUG} \
        "-Dws.output.encoding=console" \
        "-Dcom.ibm.ws.scripting.apptimeout=1800" \
        "-Djava.util.logging.manager=com.ibm.ws.bootstrap.WsLogManager" \
        "-Djava.util.logging.configureByServer=true" \
        "-Dcom.ibm.websphere.thinclient=true" \
        ${PERFJAVAOPTIONS} \
        "-Dcom.ibm.ws.scripting.wsadminprops=${WSADMIN_PROPERTIES}" \
        "-Duser.install.root=${WAS_HOME}" \
        "-Dwas.install.root=${WAS_HOME}" \
        "-Dcom.ibm.ws.scripting.exceptionPropagation=thrown" \
        -classpath "${WSADMIN_CLASS_PATH}" \
        com.ibm.ws.scripting.WasxShell
    return $?
}

run_script() {
    ${JAVA_HOME}/jre/bin/java \
        "-Dcom.ibm.ws.scripting.defaultLang=jython" \
        "-Dcom.ibm.ws.scripting.usejython21=${USE_JYTHON_21}" \
        "-Dcom.ibm.ws.scripting.traceString=com.ibm.*=all=disabled" \
        "-Duser.root=${USER_ROOT}" \
        "-Dpython.path=${PYTHON_PATH}" \
        "-Dpython.cachedir=${JYTHON_CACHEDIR}" \
        "-Djava.io.tmpdir=${TMPDIR}" \
        "-Dwebsphere.workspace.root=${WORKSPACE}" \
        "-Dcom.ibm.ws.scripting.profiles=${WDR_PROFILE}" \
        "-Dcom.ibm.SOAP.ConfigURL=file://${SOAP_PROPERTIES}" \
        "-Dcom.ibm.SSL.ConfigURL=file://${SSL_CLIENT_PROPS}" \
        ${WAS_DEBUG} \
        "-Dws.output.encoding=console" \
        "-Dcom.ibm.ws.scripting.apptimeout=1800" \
        "-Djava.util.logging.manager=com.ibm.ws.bootstrap.WsLogManager" \
        "-Djava.util.logging.configureByServer=true" \
        "-Dcom.ibm.websphere.thinclient=true" \
        ${PERFJAVAOPTIONS} \
        "-Dcom.ibm.ws.scripting.wsadminprops=${WSADMIN_PROPERTIES}" \
        "-Duser.install.root=${WAS_HOME}" \
        "-Dwas.install.root=${WAS_HOME}" \
        "-Dcom.ibm.ws.scripting.exceptionPropagation=thrown" \
        -classpath "${WSADMIN_CLASS_PATH}" \
        com.ibm.ws.scripting.WasxShell \
        -f "${WDR_SCRIPT}" $*
    return $?
}

run() {
    if [ "${WDR_SCRIPT}" == "" ] ; then
        run_interactive
        return $?
    else
        run_script $*
        return $?
    fi
}

main() {
    WDR_HOME=`dirname $0`
    WAS_DEBUG=""

    WAS_RUNTIME=$1
    shift
    TARGET_ENV=$1
    shift
    WDR_SCRIPT=$1
    shift
    if [ "${TARGET_ENV}" == "" ]; then
        usage
        exit 1
    fi
    setup || return 1
    run $*
    return $?
}

main $*
exit $?

@echo off

setlocal

set WDR_HOME=%~dp0
set WAS_DEBUG=

set WAS_RUNTIME=%1
shift
set TARGET_ENV=%1
shift
set WDR_SCRIPT=%1
shift

call %WDR_HOME%\setenv.bat %WAS_RUNTIME% %WDR_HOME%

set WAS_JAVA_HOME=%WAS_HOME%\java

set JAVA_HOME=%WAS_JAVA_HOME%
set WAS_LOGGING_PROPERTIES=-Djava.util.logging.manager=com.ibm.ws.bootstrap.WsLogManager -Djava.util.logging.configureByServer=true
set THIN_CLIENT_PROPERTY=-Dcom.ibm.websphere.thinclient=true
set CONSOLE_ENCODING_PROPERTY=-Dws.output.encoding=console
set SHELL=com.ibm.ws.scripting.WasxShell
set PERFJAVAOPTIONS=-Xms128m -Xmx512m -Xj9 -Xquickstart

set JYTHON_CACHEDIR=-Dpython.cachedir=%USERPROFILE%\.wdr\cache\%RUNTIME_NAME%
set TMPDIR_PROPERTY=-Djava.io.tmpdir=%USERPROFILE%\.wdr\tmp\%TARGET_ENV%

set USER_ROOT=%USERPROFILE%\.wdr\environments\%TARGET_ENV%
set WSADMIN_PROPERTIES=%USER_ROOT%\wsadmin.properties
set SOAP_PROPERTIES=%USER_ROOT%\soap.properties
set SSL_CLIENT_PROPS=%USER_ROOT%\ssl.client.props

set RC=0
if not exist %USER_ROOT% (
echo "Environment %TARGET_ENV% does not exist"
set RC=1
goto end
)

:user_root_exists

if not exist %WSADMIN_PROPERTIES% (
echo "Environment %TARGET_ENV% is not complete"
echo "%WSADMIN_PROPERTIES% not found"
set RC=1
)


if not exist %SOAP_PROPERTIES% (
echo "Environment %TARGET_ENV% is not complete"
echo "%SOAP_PROPERTIES% not found"
set RC=1
)

:soap_properties_exists

if not exist %SSL_CLIENT_PROPS% (
echo "Environment %TARGET_ENV% is not complete"
echo "%SSL_CLIENT_PROPS% not found"
set RC=1
)

:ssl_client_props_exists

if %RC% neq 0 goto end

set USER_ROOT_PROPERTY=-Duser.root=%USER_ROOT:\=/%
set WSADMIN_PROPERTIES_PROPERTY=-Dcom.ibm.ws.scripting.wsadminprops=%WSADMIN_PROPERTIES%
set SOAP_PROPERTIES_PROPERTY=-Dcom.ibm.SOAP.ConfigURL=file:///%SOAP_PROPERTIES:\=/%
set SSL_CLIENT_PROPS_PROPERTY=-Dcom.ibm.SSL.ConfigURL=file:///%SSL_CLIENT_PROPS:\=/%
if "%CUSTOM_PROFILE%" == "" (
set WDR_PROFILE_PROPERTY=-Dcom.ibm.ws.scripting.profiles=%WDR_HOME%profile.py
) else (
set WDR_PROFILE_PROPERTY=-Dcom.ibm.ws.scripting.profiles=%WDR_HOME%profile.py:%CUSTOM_PROFILE%
)

:: required to activate fix PM80400
:: see: http://www-01.ibm.com/support/docview.wss?uid=swg1PM80400
set WSADMIN_EXCEPTION_PROPAGATION=-Dcom.ibm.ws.scripting.exceptionPropagation=thrown

set WSADMIN_TRACE_STRING="-Dcom.ibm.ws.scripting.traceString=com.ibm.*=all=disabled"

set PYTHON_PATH=-Dpython.path=%WAS_HOME%\optionalLibraries\jython\Lib;%WDR_HOME%\lib\common

if "%JYTHON_VERSION%" == "2.1" (
set PYTHON_PATH=%PYTHON_PATH%;%WDR_HOME%\lib\legacy
)

if not "%EXTRA_PYTHON_PATH%" == "" (
set PYTHON_PATH=%PYTHON_PATH%;%EXTRA_PYTHON_PATH%
)

if "%TARGET_ENV%" == "" goto usage
if "%WDR_SCRIPT%" == "" goto interactive
goto script

:usage
echo Usage:
echo wdr.bat environment [script]
set RC=1
goto end

:interactive
%JAVA_HOME%\bin\java %WSADMIN_TRACE_STRING% %USER_ROOT_PROPERTY% %PYTHON_PATH% %JYTHON_CACHEDIR% %WDR_PROFILE_PROPERTY% %SOAP_PROPERTIES_PROPERTY% %SSL_CLIENT_PROPS_PROPERTY% %WAS_DEBUG% %CONSOLE_ENCODING_PROPERTY% %WAS_LOGGING_PROPERTIES% %THIN_CLIENT_PROPERTY% %PERFJAVAOPTIONS% %WSADMIN_PROPERTIES_PROPERTY% -Duser.install.root=%WAS_HOME:\=/% -Dwas.install.root=%WAS_HOME:\=/% %WSADMIN_EXCEPTION_PROPAGATION% -cp %WSADMIN_CLASS_PATH% %SHELL% %1 %2 %3 %4 %5 %6 %7
set RC=%ERRORLEVEL%
goto end

:script
%JAVA_HOME%\bin\java %WSADMIN_TRACE_STRING% %USER_ROOT_PROPERTY% %PYTHON_PATH% %JYTHON_CACHEDIR% %WDR_PROFILE_PROPERTY% %SOAP_PROPERTIES_PROPERTY% %SSL_CLIENT_PROPS_PROPERTY% %WAS_DEBUG% %CONSOLE_ENCODING_PROPERTY% %WAS_LOGGING_PROPERTIES% %THIN_CLIENT_PROPERTY% %PERFJAVAOPTIONS% %WSADMIN_PROPERTIES_PROPERTY% -Duser.install.root=%WAS_HOME:\=/% -Dwas.install.root=%WAS_HOME:\=/% %WSADMIN_EXCEPTION_PROPAGATION% -cp %WSADMIN_CLASS_PATH% %SHELL% -f %WDR_SCRIPT% %1 %2 %3 %4 %5 %6 %7 %8 %9
set RC=%ERRORLEVEL%
goto end

:end

endlocal

exit /b %RC%


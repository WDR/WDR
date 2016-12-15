@echo off

call :main %* & exit /b

:err
    setlocal
    echo %* 1>&2
    exit /b

:usage
    setlocal
    call :err Usage:
    call :err wdr environment [script] [script-args]
    exit /b

:file_runtimes
    call :err  ######################################################################
    call :err  ##       Runtime setup using runtimes.bat is deprecated             ##
    call :err  ##           and will be removed in the next version                ##
    call :err  ######################################################################

    call %WDR_HOME%\runtimes.default.bat
    call %WDR_HOME%\runtimes.bat

    if [%WAS_RUNTIME%] == [was61] set RUNTIME_NAME=was61
    if [%WAS_RUNTIME%] == [was61_client] set RUNTIME_NAME=was61

    if [%WAS_RUNTIME%] == [was7] set RUNTIME_NAME=was70
    if [%WAS_RUNTIME%] == [was7_client] set RUNTIME_NAME=was70
    if [%WAS_RUNTIME%] == [was70] set RUNTIME_NAME=was70
    if [%WAS_RUNTIME%] == [was70_client] set RUNTIME_NAME=was70

    if [%WAS_RUNTIME%] == [was8] set RUNTIME_NAME=was80
    if [%WAS_RUNTIME%] == [was8_client] set RUNTIME_NAME=was80
    if [%WAS_RUNTIME%] == [was80] set RUNTIME_NAME=was80
    if [%WAS_RUNTIME%] == [was80_client] set RUNTIME_NAME=was80

    if [%WAS_RUNTIME%] == [was85] set RUNTIME_NAME=was85
    if [%WAS_RUNTIME%] == [was85_client] set RUNTIME_NAME=was85

    if [%WAS_RUNTIME%] == [was855] set RUNTIME_NAME=was855
    if [%WAS_RUNTIME%] == [was855_client] set RUNTIME_NAME=was855

    if [%WAS_RUNTIME%] == [was90] set RUNTIME_NAME=was90
    if [%WAS_RUNTIME%] == [was90_client] set RUNTIME_NAME=was90

    if [%RUNTIME_NAME%] == [was61] (
        set WAS_HOME=%WAS61_RUNTIME_HOME%
        set WAS_JAVA_HOME=%WAS61_JAVA_HOME%
        set WSADMIN_CLASS_PATH=%WAS61_RUNTIME_HOME%\runtimes\com.ibm.ws.admin.client_6.1.0.jar;%WAS61_RUNTIME_HOME%\plugins\com.ibm.ws.security.crypto_6.1.0.jar
        set JYTHON_VERSION=%WAS61_JYTHON_VERSION%
    ) else if [%RUNTIME_NAME%] == [was70] (
        set WAS_HOME=%WAS70_RUNTIME_HOME%
        set WAS_JAVA_HOME=%WAS70_JAVA_HOME%
        set WSADMIN_CLASS_PATH=%WAS70_JAVA_HOME%\runtimes\com.ibm.ws.admin.client_7.0.0.jar;%WAS70_JAVA_HOME%\plugins\com.ibm.ws.security.crypto.jar
        set JYTHON_VERSION=%WAS70_JYTHON_VERSION%
    ) else if [%RUNTIME_NAME%] == [was80] (
        set WAS_HOME=%WAS80_RUNTIME_HOME%
        set WAS_JAVA_HOME=%WAS80_JAVA_HOME%
        set WSADMIN_CLASS_PATH=%WAS80_JAVA_HOME%\runtimes\com.ibm.ws.admin.client_8.0.0.jar;%WAS80_JAVA_HOME%\plugins\com.ibm.ws.security.crypto.jar
        set JYTHON_VERSION=%WAS80_JYTHON_VERSION%
    ) else if [%RUNTIME_NAME%] == [was85] (
        set WAS_HOME=%WAS85_RUNTIME_HOME%
        set WAS_JAVA_HOME=%WAS85_JAVA_HOME%
        set WSADMIN_CLASS_PATH=%WAS85_RUNTIME_HOME%\runtimes\com.ibm.ws.admin.client_8.5.0.jar;%WAS85_RUNTIME_HOME%\plugins\com.ibm.ws.security.crypto.jar
        set JYTHON_VERSION=%WAS85_JYTHON_VERSION%
    ) else if [%RUNTIME_NAME%] == [was855] (
        set WAS_HOME=%WAS855_RUNTIME_HOME%
        set WAS_JAVA_HOME=%WAS855_JAVA_HOME%
        set WSADMIN_CLASS_PATH=%WAS855_RUNTIME_HOME%\runtimes\com.ibm.ws.admin.client_8.5.0.jar;%WAS855_RUNTIME_HOME%\plugins\com.ibm.ws.security.crypto.jar
        set JYTHON_VERSION=%WAS855_JYTHON_VERSION%
    ) else if [%RUNTIME_NAME%] == [was90] (
        set WAS_HOME=%WAS90_RUNTIME_HOME%
        set WAS_JAVA_HOME=%WAS90_JAVA_HOME%
        set WSADMIN_CLASS_PATH=%WAS90_RUNTIME_HOME%\runtimes\com.ibm.ws.admin.client_9.0.jar;%WAS90_RUNTIME_HOME%\plugins\com.ibm.ws.security.crypto.jar
        set JYTHON_VERSION=%WAS90_JYTHON_VERSION%
    ) else (
        call :err  Unknown runtime %WAS_RUNTIME%
        exit /b 1
    )
    exit /b 0


:dir_runtimes
    if exist %USERPROFILE%\.wdr\runtimes\%WAS_RUNTIME%.bat (
        call %USERPROFILE%\.wdr\runtimes\%WAS_RUNTIME%.bat
    ) else if exist %WDR_HOME%\runtimes\%WAS_RUNTIME%.bat (
        call %WDR_HOME%\runtimes\%WAS_RUNTIME%.bat
    ) else if exist %WDR_HOME%\runtimes.default\%WAS_RUNTIME%.bat (
        call %WDR_HOME%\runtimes.default\%WAS_RUNTIME%.bat
    ) else (
        call :err  Unknown runtime %WAS_RUNTIME%
        exit /b 1
    )
    set RUNTIME_NAME=%WAS_RUNTIME%
    exit /b 0


:runtimes
    if exist "%WDR_HOME%\runtimes.bat" (
        call :file_runtimes || exit /b
    ) else (
        call :dir_runtimes || exit /b
    )
    if [%WAS_JAVA_HOME%] == [] (
        set WAS_JAVA_HOME=%WAS_HOME%\java
    )
    if [%JYTHON_HOME%] == [] ; then
        set JYTHON_HOME=%WAS_HOME%/optionalLibraries/jython
    fi
    if [%JYTHON_PATH%] == [] (
        set JYTHON_PATH=%JYTHON_HOME%\Lib
        set JYTHON_PATH=%JYTHON_PATH%;%JYTHON_HOME%\Lib\site-packages
    )
    exit /b


:setup
    call :runtimes || exit /b 1
    set JAVA_HOME=%WAS_JAVA_HOME%
    set WSADMIN_CLASS_PATH=%WSADMIN_CLASS_PATH%
    set JYTHON_VERSION=%JYTHON_VERSION%

    if [%PERFJAVAOPTIONS%] == [] (
        set PERFJAVAOPTIONS=-Xms128m -Xmx512m -Xj9 -Xquickstart
    )

    set JYTHON_CACHEDIR=%USERPROFILE%\.wdr\cache\%RUNTIME_NAME%
    set TMPDIR=%USERPROFILE%\.wdr\tmp\%TARGET_ENV%
    set WORKSPACE=%USERPROFILE%\.wdr\wstemp\%TARGET_ENV%

    set USER_ROOT=%USERPROFILE%\.wdr\environments\%TARGET_ENV%
    set WSADMIN_PROPERTIES=%USER_ROOT%\wsadmin.properties
    set SOAP_PROPERTIES=%USER_ROOT%\soap.properties
    set SSL_CLIENT_PROPS=%USER_ROOT%\ssl.client.props

    if not exist %USER_ROOT% (
        call :err Environment %TARGET_ENV% does not exist
        exit /b 1
    ) else (
        if not exist %WSADMIN_PROPERTIES% (
            call :err Environment %TARGET_ENV% is incomplete
            call :err %WSADMIN_PROPERTIES% not found
            exit /b 1
        )
        if not exist %SOAP_PROPERTIES% (
            call :err Environment %TARGET_ENV% is incomplete
            call :err %SOAP_PROPERTIES% not found
            exit /b 1
        )
        if not exist %SSL_CLIENT_PROPS% (
            call :err Environment %TARGET_ENV% is incomplete
            call :err %SSL_CLIENT_PROPS% not found
            exit /b 1
        )
    )

    if [%CUSTOM_PROFILE%] == [] (
        set WDR_PROFILE=%WDR_HOME%\profile.py
    ) else (
        set WDR_PROFILE=%WDR_HOME%\profile.py;%CUSTOM_PROFILE%
    )

    set JYTHON_PATH=%JYTHON_PATH%;%WDR_HOME%\lib\common
    if [%JYTHON_VERSION%] == [2.1] (
        set USE_JYTHON_21=true
        set JYTHON_PATH=%JYTHON_PATH%;%WDR_HOME%\lib\legacy
    ) else (
        set USE_JYTHON_21=false
    )

    if exist %USERPROFILE%\.wdr\lib (
        for /d %%L in (%USERPROFILE%\.wdr\lib\*) do set JYTHON_PATH=%JYTHON_PATH%;%%L
    )

    if [%EXTRA_PYTHON_PATH%] == [] (
        set JYTHON_PATH=%JYTHON_PATH%;%EXTRA_PYTHON_PATH%
    )
    set JYTHON_PATH=%JYTHON_PATH%;.
    exit /b &(
        set JAVA_HOME=%JAVA_HOME%
    )


:run_interactive
    "%JAVA_HOME%\jre\bin\java" ^
        -Dcom.ibm.ws.scripting.defaultLang=jython ^
        -Dcom.ibm.ws.scripting.usejython21=%USE_JYTHON_21% ^
        -Dcom.ibm.ws.scripting.traceString=com.ibm.*=all=disabled ^
        -Duser.root=%USER_ROOT:\=/% ^
        -Dpython.path=%JYTHON_PATH% ^
        -Dpython.home=%JYTHON_HOME% \
        -Dpython.cachedir=%JYTHON_CACHEDIR% ^
        -Djava.io.tmpdir=%TMPDIR% ^
        -Dwebsphere.workspace.root=%WORKSPACE% ^
        -Dcom.ibm.ws.scripting.profiles=%WDR_PROFILE% ^
        -Dcom.ibm.SOAP.ConfigURL=file:///%SOAP_PROPERTIES:\=/% ^
        -Dcom.ibm.SSL.ConfigURL=file:///%SSL_CLIENT_PROPS:\=/% ^
        %WAS_DEBUG% ^
        -Dws.output.encoding=console ^
        -Dcom.ibm.ws.scripting.apptimeout=1800 ^
        -Djava.util.logging.manager=com.ibm.ws.bootstrap.WsLogManager ^
        -Djava.util.logging.configureByServer=true ^
        -Dcom.ibm.websphere.thinclient=true ^
        %PERFJAVAOPTIONS% ^
        -Dcom.ibm.ws.scripting.wsadminprops=%WSADMIN_PROPERTIES% ^
        -Duser.install.root=%WAS_HOME:\=/% ^
        -Dwas.install.root=%WAS_HOME:\=/% ^
        -Dcom.ibm.ws.scripting.exceptionPropagation=thrown ^
        -cp %WSADMIN_CLASS_PATH% ^
        com.ibm.ws.scripting.WasxShell 
    exit /b


:run_script
    "%JAVA_HOME%\jre\bin\java" ^
        -Dcom.ibm.ws.scripting.defaultLang=jython ^
        -Dcom.ibm.ws.scripting.usejython21=%USE_JYTHON_21% ^
        -Dcom.ibm.ws.scripting.traceString=com.ibm.*=all=disabled ^
        -Duser.root=%USER_ROOT:\=/% ^
        -Dpython.path=%JYTHON_PATH% ^
        -Dpython.home=%JYTHON_HOME% \
        -Dpython.cachedir=%JYTHON_CACHEDIR% ^
        -Djava.io.tmpdir=%TMPDIR% ^
        -Dwebsphere.workspace.root=%WORKSPACE% ^
        %WDR_PROFILE_PROPERTY% ^
        -Dcom.ibm.SOAP.ConfigURL=file:///%SOAP_PROPERTIES:\=/% ^
        -Dcom.ibm.SSL.ConfigURL=file:///%SSL_CLIENT_PROPS:\=/% ^
        %WAS_DEBUG% ^
        -Dws.output.encoding=console ^
        -Dcom.ibm.ws.scripting.apptimeout=1800 ^
        -Djava.util.logging.manager=com.ibm.ws.bootstrap.WsLogManager ^
        -Djava.util.logging.configureByServer=true ^
        -Dcom.ibm.websphere.thinclient=true ^
        %PERFJAVAOPTIONS% ^
        -Dcom.ibm.ws.scripting.wsadminprops=%WSADMIN_PROPERTIES% ^
        -Duser.install.root=%WAS_HOME:\=/% ^
        -Dwas.install.root=%WAS_HOME:\=/% ^
        -Dcom.ibm.ws.scripting.exceptionPropagation=thrown ^
        -cp %WSADMIN_CLASS_PATH% ^
        com.ibm.ws.scripting.WasxShell ^
        -f %WDR_SCRIPT% ^
        %1 %2 %3 %4 %5 %6 %7 %8 %9
    exit /b

:run
    if [%WDR_SCRIPT%] == [] (
        call :run_interactive
    ) else (
        call :run_script
    )
    exit /b



:main
    setlocal
        set WDR_HOME=%~dp0
        set WAS_DEBUG=

        set WAS_RUNTIME=%1
        shift
        set TARGET_ENV=%1
        shift
        set WDR_SCRIPT=%1
        shift
        if [%TARGET_ENV%] == [] (
            call :usage
            exit /b 1
        )
        call :setup || exit /b
        call :run
    exit /b


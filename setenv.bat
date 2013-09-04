call %WDR_HOME%\runtimes.default.bat

if exist %WDR_HOME%\runtimes.bat call %WDR_HOME%\runtimes.bat

if "%WAS_RUNTIME%" == "was61" goto :WAS61
if "%WAS_RUNTIME%" == "was61_client" goto :WAS61
goto NOT_WAS_61

set WAS_HOME=%WAS61_RUNTIME_HOME%
set WSADMIN_CLASS_PATH=%WAS_HOME%\optionalLibraries\jython\jython.jar;%WAS_HOME%\plugins\com.ibm.ws.security.crypto_6.1.0.jar;%WAS_HOME%\runtimes\com.ibm.ws.admin.client_6.1.0.jar
set RUNTIME_NAME=was61

goto RUNTIME_SET

:NOT_WAS_61

if "%WAS_RUNTIME%" == "was7" goto :WAS7
if "%WAS_RUNTIME%" == "was7_client" goto :WAS7
if "%WAS_RUNTIME%" == "was70" goto :WAS7
if "%WAS_RUNTIME%" == "was70_client" goto :WAS7
goto NOT_WAS_7

:WAS7

set WAS_HOME=%WAS70_RUNTIME_HOME%
set WSADMIN_CLASS_PATH=%WAS_HOME%\optionalLibraries\jython\jython.jar;%WAS_HOME%\runtimes\com.ibm.ws.admin.client_7.0.0.jar;%WAS_HOME%\plugins\com.ibm.ws.security.crypto.jar
set RUNTIME_NAME=was7

goto RUNTIME_SET

:NOT_WAS_7

if "%WAS_RUNTIME%" == "was8" goto :WAS8
if "%WAS_RUNTIME%" == "was8_client" goto :WAS8
if "%WAS_RUNTIME%" == "was80" goto :WAS8
if "%WAS_RUNTIME%" == "was80_client" goto :WAS8
goto NOT_WAS_8

:WAS8

set WAS_HOME=%WAS80_RUNTIME_HOME%
set WSADMIN_CLASS_PATH=%WAS_HOME%\optionalLibraries\jython\jython.jar;%WAS_HOME%\runtimes\com.ibm.ws.admin.client_8.0.0.jar;%WAS_HOME%\plugins\com.ibm.ws.security.crypto.jar
set RUNTIME_NAME=was80

goto RUNTIME_SET

if "%WAS_RUNTIME%" == "was85" goto :WAS85
if "%WAS_RUNTIME%" == "was85_client" goto :WAS85
goto NOT_WAS_85

set WAS_HOME=%WAS85_RUNTIME_HOME%
set WSADMIN_CLASS_PATH=%WAS_HOME%\optionalLibraries\jython\jython.jar;%WAS_HOME%\runtimes\com.ibm.ws.admin.client_8.5.0.jar;%WAS_HOME%\plugins\com.ibm.ws.security.crypto.jar
set RUNTIME_NAME=was85

goto RUNTIME_SET

:NOT_WAS85

goto RUNTIME_NOT_SET

:RUNTIME_NOT_SET
echo Unknown runtime %WAS_RUNTIME%
set RC=1
goto END

:RUNTIME_SET

:END

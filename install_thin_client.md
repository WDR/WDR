---
layout: page
title: WDR installation with WebSphere Thin Client
---

Thin-client-based installation, although it is more complicated than the [server-side one](install_server.html), it has several strong advantages and is generally preferred for more complex environments, especially when you need to manage multiple WAS instances from one location:

* The installation package is being managed independently from your server software. You should be able to install the latest WAS FixPack on top of your WebSphere Application Client even if some of your servers are still some FixPack levels behind for some reason.

* Most probably you do not have to pay for WebSphere licence as long as you use WebSphere client for managing your licensed WAS installations.

  * You must check this with a lawyer. Thin client requires 2 JAR files from WAS server installation which implement wsadmin functionality.

* You can choose which version of Jython you want to use on your management node. Installing newer version of Jython simply cannot impact your server binaries. The benefits of using newer version of Jython should not be underestimated and have been described on [Jython 2.1 and wsadmin](jython21.html) page.

Most of `wsadmin` simple installations use `wsadmin.<bat|sh>` script provided by WebSphere Application Server (and derived products). Another way of setting up `wsadmin` was described by Peter Van Sickel in [Using the latest Jython with a WebSphere Application Server wsadmin thin client](http://www.ibm.com/developerworks/websphere/library/techarticles/1207_vansickel/1207_vansickel.html) in IBM developerWorks. WDR can be also used with such setup, it is actually the recommended way of installing WDR.

# Installation steps

The major installation steps include:

* Installing WebSphere Application client (together with FixPacks)

* Copying necessary JAR files from WebSphere Application Server package

* Setting up Jython in Application Client by either of these two ways:

  * Copying Jython from WebSphere server binaries

  * Installing latest Jython

* Configuring installed WAS runtimes in WDR

* Configuring access to your WAS environments

## Installing WebSphere Application Client

You must download the "GA" release of Application Client installation package from IBM Passport Advantage. It is recommended to install the latest FixPack on top of Application Client, even if your servers are not at the same FixPack level.

If your environment consists of multiple releases of WebSphere Application Server, you will need to install corresponding Application Client releases on your management node.

See official IBM documentation for detailed installation instructions.

## Copying necessary JAR files

WebSphere Application Client installation can be extended with extra JAR files an Jython runtime extracted from WebSphere Application Server installation. Detailed instruction on currently supported releases of Administration Thin Client are available at folowing links:

* [WAS v8.5 - Using the Administration Thin Client](http://pic.dhe.ibm.com/infocenter/wasinfo/v8r5/topic/com.ibm.websphere.nd.doc/ae/txml_adminclient.html)

* [WAS v8.0 - Using the Administration Thin Client](http://pic.dhe.ibm.com/infocenter/wasinfo/v8r0/topic/com.ibm.websphere.nd.doc/info/ae/ae/txml_adminclient.html)

* [WAS v7.0 - Using the Administration Thin Client](http://pic.dhe.ibm.com/infocenter/wasinfo/v7r0/topic/com.ibm.websphere.nd.doc/info/ae/ae/txml_adminclient.html)

* [WAS v6.1 - Using the Administration Thin Client](http://pic.dhe.ibm.com/infocenter/wasinfo/v6r1/topic/com.ibm.websphere.nd.doc/info/ae/ae/txml_adminclient.html)

WDR requires "Administration Thin Client" setup. It also provides you with a convenient Apache Ant script for packing and unpacking of all necessary dependencies. The script is located in ``<WDR_HOME>/utilities/client-setup/build.xml``.

The script needs to be executed on the server side once (you need to cd to the directory containing ``build.xml`` file mentioned above):

    <WAS_HOME>/bin/ws_ant.<bat|sh> pack

All required artifacts will be compressed into ``was_admin_jars.zip`` and ``was_jython.zip``. You will need to transfer these zip files to your client machine and run the scirpt again. The zip files from server machine need to reside in the same directory as ``build.xml`` file, you also need to cd to that directory:

    <WAS_CLIENT_HOME>/bin/ws_ant.<bat|sh> unpack

_Licensing implications of using Administration Thin Client are unknown. If you are aware of any documents regarding that, please open an issue in GitHub against WDR documentation._

## Configuring installed WAS runtimes in WDR

WDR can work with multiple runtimes coexisting on the same machine. The only thing you need to configure in your WDR installation is to copy ``<WDR_HOME>/runtimes.default.<bat|sh>`` into ``<WDR_HOME>/runtimes.<bat|sh>`` and modify paths accordingly.

Should you decide to use newer version of Jython, do not forget to update Jython-version-related variables.

``<WDR_HOME>/runtimes.<bat|sh>`` files look as below.

``runtimes.bat``:

{% highlight bat %}
set WAS61_RUNTIME_HOME=C:\IBM\WebSphere61\AppClient
set WAS61_JYTHON_VERSION=2.1
set WAS70_RUNTIME_HOME=C:\IBM\WebSphere7\AppClient
set WAS70_JYTHON_VERSION=2.1
set WAS80_RUNTIME_HOME=C:\IBM\WebSphere80\AppClient
set WAS80_JYTHON_VERSION=2.1
set WAS85_RUNTIME_HOME=C:\IBM\WebSphere85\AppClient
set WAS85_JYTHON_VERSION=2.1
{% endhighlight %}

``runtimes.sh``:

{% highlight bat %}
#!/bin/bash

WAS61_RUNTIME_HOME="/opt/IBM/WebSphere61/AppClient"
WAS61_JYTHON_VERSION="2.1"
WAS70_RUNTIME_HOME="/opt/IBM/WebSphere7/AppClient"
WAS70_JYTHON_VERSION="2.1"
WAS80_RUNTIME_HOME="/opt/IBM/WebSphere80/AppClient"
WAS80_JYTHON_VERSION="2.1"
WAS85_RUNTIME_HOME="/opt/IBM/WebSphere85/AppClient"
WAS85_JYTHON_VERSION="2.1"
{% endhighlight %}

## Configuring access to your WAS environments

Your WDR installation is capable of managing multiple WAS environments using different WAS runtimes.

When connecting to your WAS environments, you invoke WDR in the following way:

    <WDR_HOME>/wdr.<bat|sh> <RUNTIME_NAME> <ENVIRONMENT_NAME>
    
This example allows you to connect to your PROD WAS8 environment on Windows:

    C:\WDR\wdr.bat was8 prod_was8

On Linux/UNIX systems it would look as follows:

    /opt/WDR/wdr.sh was8 prod_was8

Each "environment" is configured in ``<HOME>/.wdr/environments/<ENVIRONMENT_NAME>`` directory using 3 property files:

* soap.properties

* wsadmin.properties

* ssl.client.props

Example files can be find below, you will need to replace following placeholders with their actual values:

* ``<SERVER_HOST_NAME>`` - hostname of your Deployment Manager (or standalone server)

* ``<SOAP_CONNECTOR_PORT>>`` - SOAP connector address of your Deployment Manager (or standalone server)

* ``<WAS_ADMIN_USERID>`` and ``<WAS_ADMIN_PASSWORD>`` - userid and password of the administrative user. If your environment is not secured, you can comment out these lines.

### soap.properties

    com.ibm.SOAP.securityEnabled=true

    com.ibm.SOAP.authenticationTarget=BasicAuth
    com.ibm.SOAP.loginUserid=<WAS_ADMIN_USERID>
    com.ibm.SOAP.loginPassword=<WAS_ADMIN_PASSWORD>

    com.ibm.SOAP.loginSource=none
    com.ibm.SOAP.requestTimeout=180
    com.ibm.ssl.alias=DefaultSSLSettings

### wsadmin.properties

    com.ibm.ws.scripting.connectionType=SOAP
    java.net.preferIPv4Stack=true
    com.ibm.ws.scripting.defaultLang=jython
    com.ibm.ws.scripting.echoparams=false
    com.ibm.ws.scripting.traceFile=tmp/wsadmin.traceout 
    com.ibm.ws.scripting.validationOutput=tmp/wsadmin.valout
    com.ibm.ws.scripting.tempdir=tmp/
    python.os=posix
    com.ibm.ws.scripting.connectionType=SOAP
    com.ibm.ws.scripting.host=<SERVER_HOST_NAME>
    com.ibm.ws.scripting.port=<SOAP_CONNECTOR_PORT>

### ssl.client.props

    #-------------------------------------------------------------------------
    # Global SSL Properties (applies to entire process)
    #-------------------------------------------------------------------------
    com.ibm.ssl.defaultAlias=DefaultSSLSettings
    com.ibm.ssl.performURLHostNameVerification=true
    com.ibm.ssl.validationEnabled=true
    com.ibm.security.useFIPS=false
    user.root=props

    #-------------------------------------------------------------------------
    # This SSL configuration is used for all client SSL connections, by default
    #-------------------------------------------------------------------------
    com.ibm.ssl.alias=DefaultSSLSettings
    com.ibm.ssl.protocol=SSL_TLS
    com.ibm.ssl.securityLevel=HIGH
    # IbmX509 trust manager has some issues with self-signed certificates
    # Ff you do not use self-signed ones, you should probably switch to IbmX509
    #com.ibm.ssl.trustManager=IbmX509
    com.ibm.ssl.trustManager=IbmPKIX
    com.ibm.ssl.keyManager=IbmX509
    com.ibm.ssl.contextProvider=IBMJSSE2
    #com.ibm.ssl.enableSignerExchangePrompt=gui
    com.ibm.ssl.enableSignerExchangePrompt=true

    # KeyStore information
    com.ibm.ssl.keyStoreName=ClientDefaultKeyStore
    com.ibm.ssl.keyStore=${user.root}/key.p12
    # feel free to change this password:
    com.ibm.ssl.keyStorePassword=WebAS
    com.ibm.ssl.keyStoreType=PKCS12
    com.ibm.ssl.keyStoreProvider=IBMJCE
    com.ibm.ssl.keyStoreFileBased=true

    # TrustStore information
    com.ibm.ssl.trustStoreName=ClientDefaultTrustStore
    com.ibm.ssl.trustStore=${user.root}/trust.p12
    # feel free to change this password:
    com.ibm.ssl.trustStorePassword=WebAS
    com.ibm.ssl.trustStoreType=PKCS12
    com.ibm.ssl.trustStoreProvider=IBMJCE
    com.ibm.ssl.trustStoreFileBased=true
    com.ibm.ssl.trustStoreReadOnly=false

# Verifying your installation and configuration

Launch your WDR client with the following command:

    <WDR_HOME>/wdr.<bat|sh> <RUNTIME_NAME> <ENVIRONMENT_NAME>

Specifically, if you want to connect to ``prod_was8`` environment using ``was8`` runtime, and you have installed WDR in ``C:\WDR``, issue this command on Windows:

    C:\WDR\wdr.bat was8 prod_was8

On Linux/UNIX systems, if you have installed WDR in ``/opt/WDR``, issue this command:

    /opt/WDR/wdr.sh was8 prod_was8

The initial connection will require you to confirm signer certificate. The certificate will be saved in ``<HOME>/.wdr/environments/<ENVIRONMENT_NAME>/trust.p12``.

WDR interactive session should open allowing you to type WDR/wsadmin commands:

    WASX7209I: Connected to process "dmgr" on node wdrDMgrNode using SOAP connector;  The type of process is: DeploymentManager
    2013-09-07 17:06:06,766 [INFO] using WDR version 0.3
    2013-09-04 17:06:06,776 [INFO] the client is connected to host wdrdmgr:8879 using SOAP connector
    2013-09-04 17:06:06,782 [INFO] the target process is wdrCell/wdrDMgrNode/dmgr
    WASX7031I: For help, enter: "print Help.help()"
    wsadmin>print getJMXMBean1(type='Server',name='dmgr').state
    STARTED
    wsadmin>reset()
    wsadmin>exit

# Part numbers of WebSphere Application Client for Linux x86 (32-bit)

Linux x86 32-bit seems to be the most commonly used platform for running WDR + WebSphere Application Client.
This section lists "part numbers" necessary to download from Passport Advantage for different releases of WebSphere Applicaiton Server.

## Version 6.1

[Download WebSphere Application Server Network Deployment Version 6.1 for the Linux operating system](http://www-01.ibm.com/support/docview.wss?uid=swg27007645)

* C88T0ML - WebSphere Application Server Network Deployment V6.1 Supplements for Linux on x86

## Version 7.0

[Download WebSphere Application Server Version 7.0 for the Linux operating system](http://www-01.ibm.com/support/docview.wss?uid=swg27012960)

* C1FZ7ML - WebSphere Application Server V7.0 Supplements for Linux on x86, 32-bit, Multilingual (1 of 2)
* C1FZ8ML - WebSphere Application Server V7.0 Supplements for Linux on x86, 32-bit, Multilingual (2 of 2)

## Version 8.0

[How to download WebSphere Application Server Network Deployment V8.0 from Passport Advantage Online](http://www-01.ibm.com/support/docview.wss?uid=swg27021166#linux)

* CZM91ML - IBM WebSphere Application Server V8.0 Supplements (1 of 4) for Multiplatform Multilingual
* CZM94ML - IBM WebSphere Application Server V8.0 Supplements (2 of 4) for Multiplatform Multilingual
* CZM95ML - IBM WebSphere Application Server V8.0 Supplements (3 of 4) for Multiplatform Multilingual
* CZXR9ML - IBM WebSphere Application Server V8.0 Supplements (4 of 4) for Multiplatform Multilingual

## Version 8.5

[How to download WebSphere Application Server Network Deployment V8.5 from Passport Advantage Online](http://www-01.ibm.com/support/docview.wss?uid=swg27024154#linux)

* CI6X0ML - IBM WebSphere Application Server V8.5 Supplements (1 of 3) for Multiplatform Multilingual
* CI6X1ML - IBM WebSphere Application Server V8.5 Supplements (2 of 3) for Multiplatform Multilingual
* CI6X2ML - IBM WebSphere Application Server V8.5 Supplements (3 of 3) for Multiplatform Multilingual

## Version 8.5.5

[How to download WebSphere Application Server Network Deployment V8.5.5 from Passport Advantage Online](http://www-01.ibm.com/support/docview.wss?uid=swg27038624#linux)

* CIK1VML - IBM WebSphere Application Server V8.5.5 Supplements (1 of 3) for Multiplatform, Multilingual
* CIK1WML - IBM WebSphere Application Server V8.5.5 Supplements (2 of 3) for Multiplatform, Multilingual
* CIK1XML - IBM WebSphere Application Server V8.5.5 Supplements (3 of 3) for Multiplatform, Multilingual

